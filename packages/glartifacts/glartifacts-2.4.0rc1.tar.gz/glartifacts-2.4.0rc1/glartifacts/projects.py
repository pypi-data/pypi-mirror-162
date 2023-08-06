import itertools
import traceback

import psycopg2
import psycopg2.extras
import yaml

from . import log
from .errors import GitlabArtifactsError, NoProjectError, InvalidCIConfigError
from .utils import memoize

GITLAB_CI_RESERVED = [
    'image',
    'services',
    'stages',
    'types',
    'before_script',
    'after_script',
    'variables',
    'cache',
    ]

def ishidden(name):
    return name.startswith('.')

def isreserved(name):
    return name.lower() in GITLAB_CI_RESERVED

class Project():
    def __init__(self, project_id, path, storage, disk_path):
        self.project_id = project_id
        self.storage = storage
        self.full_path = path
        # Projects using hashed storage have their relative path
        # in the database. If null, use the legacy path.
        if disk_path:
            self.disk_path = disk_path + '.git'
        else:
            self.disk_path = self.full_path + '.git'
        self.gl_repository = 'project-{}'.format(project_id)
        self.branches = []
        self.tags = []

    @property
    def refs(self):
        return self.branches + self.tags

    def add_branch(self, name, commit):
        branch = Ref(self, name, commit)
        self.branches.append(branch)

        return branch

    def add_tag(self, name, commit):
        tag = Ref(self, name, commit)
        self.tags.append(tag)

        return tag

    def tree_path(self, ref):
        return '{}/tree/{}'.format(
            self.full_path,
            ref.name if isinstance(ref, Ref) else ref,
            )

class Ref():
    def __init__(self, project, name, commit):
        self.project = project
        self.name = name
        self.commit = commit

        self.job_names = []

    def tree_path(self):
        return self.project.tree_path(self)

    def load_ci_config(self, config_data):
        try:
            config = yaml.safe_load(config_data)
        except yaml.YAMLError as err:
            raise InvalidCIConfigError(self) from err

        jobs = list(filter(
            lambda key: not ishidden(key) and not isreserved(key),
            config.keys()
            ))

        # gitlab-ci.yml must have at least one job
        if not jobs:
            raise InvalidCIConfigError(self)

        self.job_names = jobs

def _get_project(db, path, parent_id):
    project = None

    with db:
        with db.cursor() as cur:
            cur.execute(Query.get_project, dict(path=path, parent_id=parent_id))
            project = cur.fetchone()

    if not project:
        raise NoProjectError(path)

    return project

def _get_namespace_id(db, path_component, parent_id):
    ns = None
    with db:
        with db.cursor() as cur:
            cur.execute(Query.get_namespace, dict(path=path_component, parent_id=parent_id))
            ns = cur.fetchone()

    return ns[0] if ns else None

def _walk_namespaces(db, namespaces, project_path, parent_id=None):
    if not namespaces:
        return _get_project(db, project_path, parent_id)

    ns_path = namespaces.pop(0)
    ns_id = _get_namespace_id(db, ns_path, parent_id)
    if not ns_id:
        raise GitlabArtifactsError('No namespace "{}"'.format(ns_path))

    return _walk_namespaces(db, namespaces, project_path, ns_id)

def _filter_projects(db, project_paths, all_projects, exclude_paths):
    filtered_paths = project_paths

    if all_projects:
        filtered_paths = {
            '/'.join((p['namespace'], p['project']))
            for p in list_projects(db)
            }

    if exclude_paths:
        s_projects = set(filtered_paths)
        s_exclude = set(exclude_paths)

        # Warn user if excluded projects look bogus
        unused_excludes = s_exclude - s_projects
        for exclude in unused_excludes:
            log.warning(
                'Excluded path %s was not in the set of projects',
                exclude,
                )

        filtered_paths = s_projects - s_exclude

    return filtered_paths

@memoize(
    # memoize over project_id and commit
    key=lambda args: (args[1].project.project_id, args[1].commit,)
    )
def _get_ci_config(gitaly, ref):
    oid, _, data = gitaly.get_tree_entry(
        ref,
        '.gitlab-ci.yml',
        )

    # Gitaly returns an empty response if not found
    if not oid:
        return None

    return data

def _load_ref_config_yaml(gitaly, ref, refs_with_artifacts):
    # Only print warnings for refs with artifacts
    # that may be removed
    has_artifacts = ref.name in refs_with_artifacts

    # Load branch jobs via .gitlab-ci.yml
    config_data = _get_ci_config(gitaly, ref)
    if config_data:
        ref.load_ci_config(config_data)

        if not ref.job_names and has_artifacts:
            log.warning(
                'No jobs found in .gitlab-ci.yml for %s. '
                'All artifacts will be removed.',
                ref.tree_path()
                )
    elif has_artifacts:
        # No config for this branch means CI has been turned off
        log.warning(
            'No .gitlab-ci.yml for %s. '
            'All artifacts will be removed.',
            ref.tree_path()
            )

def find_project(db, full_path):
    namespaces = full_path.split('/')
    try:
        project_path = namespaces.pop()
        project_id, storage, disk_path = _walk_namespaces(
            db,
            namespaces,
            project_path
            )
    except Exception as err:
        raise NoProjectError(full_path) from err

    return Project(
        project_id,
        full_path,
        storage,
        disk_path,
        )

def list_projects(db):
    with db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(Query.projects_with_artifacts)
            return cur.fetchall()

def list_artifact_refs_by_project(db):
    with db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(Query.branches_with_artifacts)

            # returns { project_id: [refs] }
            # NOTE: rows must be sorted by project_id
            return {
                p: list(r['ref'] for r in b)
                for p, b in itertools.groupby(
                    cur.fetchall(),
                    lambda b: b['project_id']
                    )
                }

def projects_from_paths(db, gitaly, project_paths, all_projects=False, exclude_paths=None):
    projects = {}

    project_paths = _filter_projects(db, project_paths, all_projects, exclude_paths)

    refs_with_artifacts_by_project = list_artifact_refs_by_project(db)
    for project_path in project_paths:
        try:
            project = find_project(db, project_path)

            refs_with_artifacts = refs_with_artifacts_by_project.get(
                project.project_id,
                []
                )

            # Load git branches
            branches = gitaly.get_branches(project)
            for name, commit in branches:
                branch = project.add_branch(name, commit)
                _load_ref_config_yaml(gitaly, branch, refs_with_artifacts)

            # Load git tags
            tags = gitaly.get_tags(project)
            for name, commit in tags:
                tag = project.add_tag(name, commit)
                _load_ref_config_yaml(gitaly, tag, refs_with_artifacts)

        except (NoProjectError, InvalidCIConfigError) as e:
            # Continue loading projects even if a single project fails
            log.warning('Skipping %s. Reason: %s', project_path, str(e))
            log.debug(traceback.format_exc())
            continue

        projects[project.project_id] = project

    return projects

class Query():
    projects_with_artifacts = """
with recursive ns_paths(id, parent_id, path) as (
    select n.id, n.parent_id, n.path::text
        from namespaces as n
        where n.parent_id is NULL
    union all
    select c.id, c.parent_id, (p.path || '/' || c.path)::text as path
        from namespaces as c
        inner join ns_paths as p on p.id=c.parent_id
)
select a.project_id, p.path as project, n.path as namespace,
    count(distinct a.job_id) as artifact_count,
    coalesce(sum(a.size), 0) as artifact_size
from ci_job_artifacts as a
inner join projects as p on p.id=a.project_id
left join ns_paths as n on p.namespace_id=n.id
where a.file_type = 1
group by a.project_id, p.path, n.path
"""

    branches_with_artifacts = """
select distinct a.project_id as project_id, b.ref
from ci_job_artifacts as a
inner join ci_builds as b on b.id=a.job_id
where a.file_type = 1
order by a.project_id
"""

    get_namespace = """
select id from namespaces where path=%(path)s and
    ((%(parent_id)s is null and parent_id is null) or parent_id=%(parent_id)s)
"""

    get_project = """
select p.id, p.repository_storage, r.disk_path
from projects as p
left join project_repositories as r on r.project_id=p.id
where path=%(path)s and
    (%(parent_id)s is null or namespace_id=%(parent_id)s)
"""
