import enum
import io
import itertools
import psycopg2
import psycopg2.extras

from . import log
from .utils import indent

class ArtifactDisposition(enum.Enum):
    TAGGED = 1
    EXPIRING = 2
    ORPHANED = 3
    GOOD = 4
    OLD = 5
    NEW = 6
    ORPHANED_TAG = 7

    def __str__(self):
        return str(self.name).replace('_', ' ').lower()

class ExpirationStrategy(enum.Enum):
    # Keep good artifacts per-job
    LASTGOOD_JOB = 1

    # Keep good artifacts per-pipeline
    LASTGOOD_PIPELINE = 2

    def __str__(self):
        return self.name

    @staticmethod
    def parse(value):
        try:
            return ExpirationStrategy[value]
        except KeyError:
            return None

def _load_project_branches(cursor, projects):
    cursor.execute(
        "create temp table "
        "__project_branch_jobs (id int, ref varchar, job varchar) "
        "on commit drop"
        )

    # Get a flattened list of tab-delimited (project_id, branch_name, job_name) tuples
    items = map(
        lambda p: [
            '{}\t{}\t{}\n'.format(p.project_id, ref.name, job_name)
            for ref in p.refs
            for job_name in ref.job_names
            ],
        projects.values()
        )
    items = itertools.chain.from_iterable(items)

    # psql copy_from requires a tab-delimited fileobj one row per-line
    data = io.StringIO()
    for row in items:
        data.write(row)
    data.seek(0)
    cursor.copy_from(data, '__project_branch_jobs', columns=('id', 'ref', 'job'))

def _get_removal_strategy_query(strategy):
    if strategy == ExpirationStrategy.LASTGOOD_JOB:
        return Query.lastgood.format(Query.good_job)
    if strategy == ExpirationStrategy.LASTGOOD_PIPELINE:
        return Query.lastgood.format(Query.good_pipeline)

    raise Exception("Strategy {} not implemented".format(strategy.name))

def list_artifacts(db, projects, strategy, remove_only=False):
    strategy_query = _get_removal_strategy_query(strategy)
    action_query = Query.artifact_list.format(
        Query.artifact_definition,
        Query.identify_artifacts if remove_only else ''
        )
    sql = strategy_query + action_query
    log.debug("Running %s list artifacts query:\n  %s", strategy.name, indent(sql))

    with db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            _load_project_branches(cur, projects)
            cur.execute(sql)
            return cur.fetchall()

def remove_artifacts(db, projects, strategy):
    strategy_query = _get_removal_strategy_query(strategy)
    action_query = Query.build_expire.format(
        Query.artifact_definition,
        Query.identify_artifacts,
        )

    sql = strategy_query + action_query
    log.debug("Running %s remove artifacts query:\n  %s", strategy.name, indent(sql))

    with db:
        with db.cursor() as cur:
            _load_project_branches(cur, projects)
            cur.execute(sql)
            cur.execute(Query.job_artifact_expire)

class Query():
    # Find the date of the most recent good pipeline and job
    lastgood = """
with lastgood as (
select lg.project_id, lg.name, lg.ref, lg.pipeline_date,
    max(b.created_at) as build_date
from (
    select b.project_id, b.name, b.ref,
            max(p.created_at) as pipeline_date
    from ci_builds as b
    join __project_branch_jobs as pbj on pbj.id=b.project_id
    join ci_stages as s on s.id=b.stage_id
    join ci_pipelines as p on p.id=s.pipeline_id
    where {}
    group by b.project_id, b.name, b.ref
) as lg
join ci_builds as b on b.project_id=lg.project_id and b.name=lg.name and b.ref=lg.ref
join ci_stages as s on s.id=b.stage_id
join ci_pipelines as p on p.id=s.pipeline_id
where p.created_at = lg.pipeline_date
group by lg.project_id, lg.name, lg.ref, lg.pipeline_date
)
""".strip()

    # An artifact is old if it was created prior to the lastgood point in time
    artifact_is_old = """
(p.created_at<lastgood.pipeline_date or
(p.created_at=lastgood.pipeline_date and b.created_at<lastgood.build_date))
""".strip()

    # An artifact is lastgood if it's pipeline date and build_date match lastgood
    artifact_is_lastgood = """
(p.created_at=lastgood.pipeline_date and b.created_at=lastgood.build_date)
""".strip()

    # An artifact is orphan if it's branch or job have been removed
    artifact_is_orphan = """
(pbj.id is NULL)
""".strip()

    # Criteria that define "good" for Job or Pipeline
    good_job = "(b.status='success' or b.allow_failure)"
    good_pipeline = "(p.status='success')"

    # Set of artifacts for a list operation
    # NOTE: lastgood is left-joined, so comparisons within artifact_is
    #       terms return null rather than true or false if there is no
    #       lastgood point-in-time. In psql, null is not true, so it
    #       works fine. Adding coalesce is mathmatically correct, but
    #       may confuse the optimizer.
    artifact_definition = """
from ci_builds as b
join ci_stages as s on s.id=b.stage_id
join ci_pipelines as p on p.id=s.pipeline_id
join ci_job_artifacts as a on a.job_id=b.id
left join lastgood
    on lastgood.project_id=b.project_id and lastgood.name=b.name
        and lastgood.ref=b.ref
left join __project_branch_jobs as pbj
    on pbj.id=b.project_id and pbj.ref=b.ref and pbj.job=b.name
where a.file_type = 1 and
    b.project_id in (select distinct id from __project_branch_jobs)
""".strip()

    # Identifies expired artifacts based on a lastgood strategy
    # "expired" is defined as:
    #    Older than the lastgood pipeline OR
    #       older than the lastgood job within the lastgood pipeline
    #    Not tagged
    #    Not already expired
    #    Has artifacts file_type=1 (zip)
    identify_artifacts = """
    -- old or orphan
    and ({} or {})
    and b.tag = false
    and b.artifacts_expire_at is null
    and a.file_type = 1
""".format(
    artifact_is_old,
    artifact_is_orphan,
    ).strip()

    # Wrapper that lists identified artifacts
    artifact_list = """
select p.project_id as project_id, p.id as pipeline_id, p.status as pipeline_status,
    b.id as job_id,
    p.created_at as scheduled_at,
    b.name, b.status, b.ref,
    coalesce(a.size, 0) as size,
    case
        when (b.tag and not {0}) then 1
        when b.artifacts_expire_at is not null then 2
        when (b.tag and {0}) then 7 -- tag orphans
        when {0} then 3 -- orphans
        when {1} then 4 -- lastgood
        when {2} then 5 -- old
        else 6 -- new
    end as disposition
{{}}
{{}}
""".format(
    artifact_is_orphan,
    artifact_is_lastgood,
    artifact_is_old,
    )

    # Wrapper that sets build expiration on identified artifacts
    build_expire = """
update ci_builds as target
set artifacts_expire_at=(now() at time zone 'utc')
{}
{}
    and target.id=b.id
""".strip()

    # Transfer expiration from job to artifact
    # NOTE: GitLab started using both columns in 11.11. See #31
    job_artifact_expire = """
update ci_job_artifacts as a
set expire_at = b.artifacts_expire_at
from ci_builds as b
where b.artifacts_expire_at is not null
    and a.job_id = b.id
    and a.expire_at is null
    and a.file_type in (1,2)
""".strip()
