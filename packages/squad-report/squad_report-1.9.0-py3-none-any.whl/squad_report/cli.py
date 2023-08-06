import argparse
import os
import pathlib
import importlib
import squad_report.config
import squad_report.datasets
import squad_report.logging
import squad_report.reports
from squad_report.version import __version__
from squad_client.core.api import SquadApi
from squad_client.core.api import ApiException as SquadApiException
from squad_client.core.models import Squad, Build
from squad_client.utils import getid

logger = squad_report.logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(
        prog="squad-report", description="Create a report using data from SQUAD"
    )

    parser.add_argument(
        "--cache",
        default=0,
        type=int,
        help="Cache squad-client requests with a timeout",
    )

    parser.add_argument(
        "--token",
        default=os.environ.get("SQUAD_TOKEN", None),
        help="Authenticate to SQUAD using this token",
    )

    parser.add_argument(
        "--url",
        default=os.environ.get("SQUAD_URL", "https://qa-reports.linaro.org"),
        help="URL of the SQUAD service",
    )

    parser.add_argument(
        "--group",
        help="SQUAD group",
    )

    parser.add_argument(
        "--project",
        help="SQUAD project",
    )

    parser.add_argument(
        "--build",
        help="SQUAD build",
    )

    parser.add_argument(
        "--base-build",
        help="SQUAD build to compare to",
    )

    environments_group = parser.add_mutually_exclusive_group()
    environments_group.add_argument(
        "--environments",
        help="List of SQUAD environments to include",
    )

    environments_group.add_argument(
        "--environment-prefixes",
        help="List of prefixes of SQUAD environments to include",
    )

    suites_group = parser.add_mutually_exclusive_group()
    suites_group.add_argument(
        "--suites",
        help="List of SQUAD suites to include",
    )

    suites_group.add_argument(
        "--suite-prefixes",
        help="List of prefixes of SQUAD suites to include",
    )

    parser.add_argument(
        "--email-cc",
        help="Create the report with email cc",
    ),

    parser.add_argument(
        "--email-from",
        help="Create the report with email from",
    ),

    parser.add_argument(
        "--email-subject",
        help="Create the report with this email subject",
    ),

    parser.add_argument(
        "--email-to",
        help="Create the report with email to",
    ),

    parser.add_argument(
        "--output",
        help="Write the report to this file",
    )

    parser.add_argument(
        "--send-on",
        help="Always send an email, on failures, regressions or always",
    )

    parser.add_argument(
        "--template",
        default="report",
        help="Create the report with this template",
    )

    parser.add_argument(
        "--config",
        default=squad_report.config.CONFIG_PATH,
        help="Create the report using this configuration",
    )

    parser.add_argument(
        "--config-report-type",
        help="Set the report type to use in the local config file",
    )

    parser.add_argument(
        "--perf-report-hook",
        help="Set performance report script hook",
    )

    parser.add_argument(
        "--perf-report-hook-args",
        help="Set performance script comma separated arguments",
    )

    parser.add_argument(
        "--unfinished",
        action="store_true",
        default=False,
        help="Create a report even if a build is not finished",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print out the version",
    )

    return parser


def report():
    parser = get_parser()
    args = parser.parse_args()

    if (
        args.group is None
        and args.project is None
        and args.build is None
        and args.version is False
    ):
        parser.print_help()
        return -1

    if args.version:
        print(f"squad_report version: {__version__}")
        return 0

    try:
        SquadApi.configure(url=args.url, token=args.token, cache=args.cache)
    except SquadApiException as sae:
        logger.error("Failed to configure the squad api: %s", sae)
        return -1

    squad = Squad()

    # This will setup config options
    config = squad_report.config.setup_config(args)
    group = squad.group(config.squad_group)
    project = group.project(config.squad_project)
    build = project.build(args.build)
    base_build = None

    if args.base_build:
        base_build = project.build(args.base_build)

        if not base_build:
            logger.error(f"Base build {args.base_build} does not exist.")
            return -1
    else:
        try:
            base_build_id = getid(build.status.baseline)
            base_build = Build().get(base_build_id)
        except TypeError:
            logger.error(f"Build {build.version} does not have a required base build.")
            return -1

    if not args.unfinished:
        if not build.finished:
            logger.error(
                f"Build {build.version} has not yet finished. Use --unfinished to force a report."
            )
            return -1

        if not base_build.finished:
            logger.error(
                f"Build {base_build.version} has not yet finished."
                "Use --unfinished to force a report."
            )
            return -1

    results = squad_report.datasets.results(
        group, project, build, base_build, args.unfinished
    )
    test_changes = squad_report.datasets.test_changes(
        group, project, build, base_build, args.unfinished
    )
    metric_changes = squad_report.datasets.metric_changes(
        group,
        project,
        build,
        base_build,
        args.unfinished,
    )
    mdu = squad_report.datasets.metric_download_urls(
        group, project, build, base_build, args.unfinished
    )

    if config.filter_environments:
        results = squad_report.dataframe.filter_isin(
            results, "environment", tuple(config.filter_environments.split(","))
        )
        test_changes = squad_report.dataframe.filter_isin(
            test_changes, "environment", tuple(config.filter_environments.split(","))
        )
        metric_changes = squad_report.dataframe.filter_isin(
            metric_changes, "environment", tuple(config.filter_environments.split(","))
        )

    if config.filter_suites:
        results = squad_report.dataframe.filter_isin(
            results, "suite", tuple(config.filter_suites.split(","))
        )
        test_changes = squad_report.dataframe.filter_isin(
            test_changes, "suite", tuple(config.filter_suites.split(","))
        )
        metric_changes = squad_report.dataframe.filter_isin(
            metric_changes, "suite", tuple(config.filter_suites.split(","))
        )

    if config.filter_environment_prefixes:
        results = squad_report.dataframe.filter_startswith(
            results, "environment", tuple(config.filter_environment_prefixes.split(","))
        )
        test_changes = squad_report.dataframe.filter_startswith(
            test_changes,
            "environment",
            tuple(config.filter_environment_prefixes.split(",")),
        )
        metric_changes = squad_report.dataframe.filter_startswith(
            metric_changes,
            "environment",
            tuple(config.filter_environment_prefixes.split(",")),
        )

    if config.filter_suite_prefixes:
        results = squad_report.dataframe.filter_startswith(
            results, "suite", tuple(config.filter_suite_prefixes.split(","))
        )
        test_changes = squad_report.dataframe.filter_startswith(
            test_changes, "suite", tuple(config.filter_suite_prefixes.split(","))
        )
        metric_changes = squad_report.dataframe.filter_startswith(
            metric_changes, "suite", tuple(config.filter_suite_prefixes.split(","))
        )

    if config.perf_report_hook:
        perf_report_args = config.perf_report_hook_args.split(",")
        if len(perf_report_args) < 1:
            logger.error("Not enough perf-report-hook-args parameters supplied")
            return -1

        if not os.path.isdir(perf_report_args[0]):
            logger.error(f"Could not find repo in {config.perf_report_args[0]}.")
            return -1

        try:
            perf_module = importlib.import_module("scripts." + config.perf_report_hook)
        except (NameError, ModuleNotFoundError):
            logger.error("Could not load performance script.")
            return -1

        try:
            text = perf_module.create_perf_report(
                config,
                perf_report_args,
                group,
                project,
                build,
                base_build,
                args.environments,
                args.suites,
            )
        except AttributeError:
            logger.error("Could not call performance script's method")
            return -1
    else:
        text = squad_report.reports.create_report(
            config,
            group,
            project,
            build,
            base_build,
            test_changes,
            metric_changes,
            mdu,
            results,
        )

    if text:
        if config.output:
            pathlib.Path(config.output).write_text(text)
            print("Report created in", config.output)
        else:
            print(text)
    else:
        print(
            "Report was skipped to be generated, due to 'send_on': %s "
            "condition" % config.send_on
        )

    return 0
