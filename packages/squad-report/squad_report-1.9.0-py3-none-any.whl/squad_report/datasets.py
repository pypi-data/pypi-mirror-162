from collections import defaultdict
import pandas as pd
from squad_report.logging import getLogger
from squad_client.core.models import Environment, Suite, TestRun
from squad_client.utils import first, getid

logger = getLogger(__name__)


def metric_download_urls(group, project, build, base_build, unfinished):
    logger.debug("Fetching metric download_urls")
    changes = project.compare_builds(
        base_build.id, build.id, by="metrics", force=unfinished
    )

    urls = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    )
    for change in changes.keys():
        for environment in changes[change].keys():
            for suite, metrics in changes[change][environment].items():
                for metric in metrics:
                    m = first(build.metrics(name=metric, count=1))
                    tr = TestRun(getid(m.test_run))
                    if hasattr(tr.metadata, "download_url"):
                        urls[change][environment][suite][
                            metric
                        ] = tr.metadata.download_url

    return urls


def metric_changes(group, project, build, base_build, unfinished):
    logger.debug("Fetching metric changes")
    changes = project.compare_builds(
        base_build.id, build.id, by="metrics", force=unfinished
    )

    change_data = []
    for change in changes.keys():
        for environment in changes[change].keys():
            for suite, metrics in changes[change][environment].items():
                for metric in metrics:
                    change_data.append(
                        {
                            "group": group.slug,
                            "project": project.slug,
                            "build": build.version,
                            "base_build": base_build.version,
                            "environment": environment,
                            "suite": suite,
                            "metric": metric,
                            "change": change,
                        }
                    )

    data = pd.DataFrame(change_data)

    if not data.empty:
        data.sort_values(by=["environment", "suite", "metric"], inplace=True)

    return data


def test_changes(group, project, build, base_build, unfinished):
    logger.debug("Fetching changes...")
    changes = project.compare_builds(base_build.id, build.id, force=unfinished)

    change_data = []
    for change in changes.keys():
        for environment in changes[change].keys():
            for suite, tests in changes[change][environment].items():
                for test in tests:
                    change_data.append(
                        {
                            "group": group.slug,
                            "project": project.slug,
                            "build": build.version,
                            "base_build": base_build.version,
                            "environment": environment,
                            "suite": suite,
                            "test": test,
                            "change": change,
                        }
                    )

    data = pd.DataFrame(change_data)

    if not data.empty:
        data.sort_values(by=["environment", "suite", "test"], inplace=True)

    return data


def results(group, project, build, base_build, unfinished):
    logger.debug("Fetching results...")
    tests = build.tests(fields="build,environment,short_name,status,suite").values()

    result_data = []
    environments = {}
    suites = {}
    for test in tests:
        if test.environment not in environments:
            environments[test.environment] = Environment().get(
                _id=getid(test.environment)
            )
        if test.suite not in suites:
            suites[test.suite] = Suite().get(_id=getid(test.suite))

        environment = environments[test.environment]
        suite = suites[test.suite]
        result_data.append(
            {
                "group": group.slug,
                "project": project.slug,
                "build": build.version,
                "base_build": base_build.version,
                "environment": environment.slug,
                "suite": suite.slug,
                "test": test.short_name,
                "status": test.status,
            }
        )

    data = pd.DataFrame(result_data)
    data.sort_values(by=["environment", "suite", "test"], inplace=True)

    return data
