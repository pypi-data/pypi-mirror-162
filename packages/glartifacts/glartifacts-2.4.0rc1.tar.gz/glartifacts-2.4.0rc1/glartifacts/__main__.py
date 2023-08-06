import argparse
import logging
import os
import pwd
import sys
import traceback

import psycopg2

from . import log, utils
from .config import load_config
from .errors import GitlabArtifactsError
from .gitaly import GitalyClient
from .projects import list_projects, projects_from_paths
from .artifacts import list_artifacts, remove_artifacts, ExpirationStrategy, ArtifactDisposition
from .version import __version__

def default_settings():
    return utils.OutputSettings(humanize=True, delimiter=None)

def switch_user():
    gluser = pwd.getpwnam('git')
    os.setgid(gluser.pw_gid)
    os.setuid(gluser.pw_uid)

def get_args():
    parser = argparse.ArgumentParser(
        prog='glartifacts',
        description='Tools for managing GitLab artifacts')
    parser.add_argument(
        '-d', '--debug',
        action="store_true",
        help="show detailed debug information")
    parser.add_argument(
        '--verbose',
        action="store_true",
        help="show additional information")
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s v'+__version__)

    commands = parser.add_subparsers(dest='command', title='Commands', metavar='')
    listcmd = commands.add_parser("list", help='List build artifacts')
    listcmd.add_argument(
        "projects",
        metavar='PROJECT',
        nargs='*',
        help='paths to the projects whose artifacts should be listed')
    listcmd.add_argument(
        '-a', '--all',
        action='store_true',
        help='list artifacts from all projects')
    listcmd.add_argument(
        '-e', '--exclude',
        action='store',
        nargs='+',
        metavar='PROJECT',
        help='paths to the projects whose artifacts should not by listed')
    listcmd.add_argument(
        '-m', '--machine-readable',
        action='store_true',
        help='use machine readable formats to print dates and file sizes and strip chrome')
    listcmd.add_argument(
        '-d', '--delimiter',
        action='store',
        help='separates table columns using the specified character')
    listcmd.add_argument(
        '-s', '--short',
        action='store_true',
        help='use a short list format that only prints project names')

    removecmd = commands.add_parser("remove", help='Remove old build artifacts for a project')
    removecmd.add_argument(
        'projects',
        metavar='PROJECT',
        nargs='*',
        help='paths to the projects whose artifacts should be removed')
    removecmd.add_argument(
        '--dry-run',
        action="store_true",
        help='identify artifacts to be removed, but do not make any changes')
    removecmd.add_argument(
        '-a', '--all',
        action='store_true',
        help='remove artifacts from all projects')
    removecmd.add_argument(
        '-e', '--exclude',
        action='store',
        nargs='+',
        metavar='PROJECT',
        help='paths to the projects whose artifacts should not be removed')

    # Add arguments shared by list and remove
    for cmd in [listcmd, removecmd]:
        cmd.add_argument(
            '--strategy',
            type=ExpirationStrategy.parse,
            choices=list(ExpirationStrategy),
            default=ExpirationStrategy.LASTGOOD_PIPELINE,
            help=(
                'select the expiration strategy used to identify old artifacts '
                '(default: LASTGOOD_PIPELINE)'
                ))

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return None

    if args.debug:
        log.setLevel(logging.DEBUG)
    elif args.verbose:
        log.setLevel(logging.INFO)

    return args

def show_projects(db, short_format=False, exclude_paths=None, output_settings=None):
    projects = list_projects(db)
    if exclude_paths:
        projects = [
            p for p in projects
            if not p['namespace']+'/'+p['project'] in exclude_paths
            ]

    if not projects:
        raise GitlabArtifactsError("No projects were found with artifacts")

    if short_format:
        names = {'/'.join((p['namespace'], p['project'])) for p in projects}
        print("\n".join(names))
        return

    settings = output_settings or default_settings()
    heading = ['Project', 'Id', 'Jobs with Artifacts', 'Total Size']
    fmt_id = utils.humanize_id if settings.humanize else utils.machine_id
    fmt_size = utils.humanize_size if settings.humanize else utils.machine_size
    transforms = [
        None,
        fmt_id,
        None,
        fmt_size,
        ]
    totals = [None]*2 + [sum, sum]
    rows = []
    for p in projects:
        rows.append([
            '/'.join((p['namespace'], p['project'])),
            p['project_id'],
            p['artifact_count'],
            p['artifact_size'],
            ])
    utils.tabulate(
        heading,
        rows,
        display_transforms=transforms,
        totals=totals,
        sortby=dict(key=lambda r: r[0]),
        settings=settings
        )

def show_artifacts(
        projects, artifacts, scope, short_format=False, strategy=None, output_settings=None):
    project_names = [
        '{} #{}'.format(p.full_path, project_id)
        for project_id, p in projects.items()
        ]
    projects = ", ".join(sorted(project_names))
    if not artifacts:
        raise GitlabArtifactsError("No "+scope+" were found for "+projects)

    if short_format:
        print("\n".join({r['name'] for r in artifacts}))
        return

    settings = output_settings or default_settings()
    if settings.humanize:
        print("Listing", scope, "for", projects, end="")
        if strategy:
            print(" using", strategy, "strategy", end="")
        print("\n")

    heading = [
        'Project',
        'Pipeline',
        'Status',
        'Job',
        '' if settings.humanize else 'Job Id',
        'Status',
        'Ref',
        'Scheduled At',
        'Artifacts',
        'Size'
        ]
    fmt_id = utils.humanize_id if settings.humanize else utils.machine_id
    fmt_size = utils.humanize_size if settings.humanize else utils.machine_size
    fmt_time = utils.humanize_datetime if settings.humanize else utils.machine_datetime
    transforms = [
        fmt_id,
        fmt_id,
        None,
        None,
        fmt_id,
        None,
        None,
        fmt_time,
        None,
        fmt_size,
        ]
    totals = [None]*9+[sum]
    rows = []
    for r in artifacts:
        rows.append([
            r['project_id'],
            r['pipeline_id'],
            r['pipeline_status'],
            r['name'],
            r['job_id'],
            r['status'],
            r['ref'],
            r['scheduled_at'],
            ArtifactDisposition(r['disposition']),
            r['size'],
            ])
    utils.tabulate(
        heading,
        rows,
        display_transforms=transforms,
        totals=totals,
        sortby=[
            dict(key=lambda r: r[6], reverse=True),
            dict(key=lambda r: r[1], reverse=True),
            dict(key=lambda r: r[0], reverse=True),
            ],
        settings=settings
        )

def run_command(db, gitaly, args):
    projects = {}

    if args.projects or args.all:
        projects = projects_from_paths(
            db,
            gitaly,
            project_paths=args.projects,
            all_projects=args.all,
            exclude_paths=args.exclude)

        if not projects:
            raise GitlabArtifactsError('No valid projects specified')

    if args.command == 'list':
        # initalize output formats
        settings = utils.OutputSettings.from_args(args)

        if projects:
            artifacts = list_artifacts(
                db,
                projects,
                strategy=args.strategy
                )
            show_artifacts(projects, artifacts, "artifacts", args.short, output_settings=settings)
        else:
            show_projects(db, args.short, args.exclude, output_settings=settings)
    elif args.command == 'remove':
        if not projects:
            raise GitlabArtifactsError('No valid projects specified')

        if args.dry_run:
            artifacts = list_artifacts(
                db,
                projects,
                args.strategy,
                remove_only=True,
                )
            show_artifacts(
                projects,
                artifacts,
                "old or orphaned artifacts",
                strategy=args.strategy
                )
        else:
            with db:
                remove_artifacts(db, projects, args.strategy)
    else:
        raise Exception("Command {} not implemented".format(args.command))

def glartifacts():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.WARN,
        format='%(levelname)s: %(message)s')

    args = get_args()
    if not args:
        sys.exit(1)

    config = load_config()

    try:
        switch_user()
    except PermissionError:
        log.error("Permission Denied. Unable to switch to GitLab's git user.")
        return 1

    db = None
    try:
        db = psycopg2.connect(
            database=config['postgres']['dbname'],
            user=config['postgres']['user'],
            host=config['postgres']['host'],
            port=config['postgres']['port'],
            )

        with GitalyClient(config['gitaly']['address']) as gitaly:
            run_command(db, gitaly, args)

    finally:
        if db:
            db.close()

    return 0

def main():
    try:
        sys.exit(glartifacts())
    except Exception:  # pylint: disable=broad-except
        log.error(sys.exc_info()[1])
        if log.level == logging.DEBUG:
            traceback.print_exc()

        sys.exit(1)

if __name__ == '__main__':
    main()
