import jinja2
from os.path import expanduser, dirname, join
import subprocess
import json
from squad_report.reports import squad_build_url
from . import squad_get
import squad_report.logging

logger = squad_report.logging.getLogger(__name__)

te = jinja2.Environment(
    extensions=["jinja2.ext.loopcontrols"],
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader(
                join(dirname(__file__), "..", "squad_report", "templates")
            ),
            jinja2.FileSystemLoader(expanduser("~/.config/squad_report/templates")),
        ]
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=jinja2.StrictUndefined,
)


def create_perf_report(
    config, perf_report_args, group, project, build, base_build, environments, suites
):
    mmtests_directory = perf_report_args[0]

    path_to_mmtests = join(dirname(__file__), "../../", mmtests_directory)
    path_to_compare = join(path_to_mmtests, "compare-kernels.sh")

    environment = environments.split(",")[0]
    suite = suites.split(",")[0]
    testname = suite.split("-")[1]

    dict_data = squad_get.get_data(base_build, build, environment, suite)
    json_files = []

    for key in dict_data:
        json_filename = key + ".json"
        with open(json_filename, "w") as fp:
            json_files.append(json_filename)
            json.dump(dict_data[key], fp)

    cmp_kern_out = b""

    for jsonfile in json_files:
        cmd_compare_kernel = [
            f"{path_to_compare}",
            "--from-json",
            jsonfile,
        ]

        cmp_kern_out += subprocess.check_output(cmd_compare_kernel)

    full_output = []
    regression = []
    for line in cmp_kern_out.splitlines():
        full_output.append(line.decode())
        if "*" in line.decode():
            regression.append(line.decode())

    doc_link = (
        "https://github.com/gormanm/mmtests/blob/master/docs/regression-detection.md"
    )

    config_values = {"item": [], "test": "test=" + testname, "cmd": ""}
    seen_cmds = []

    try:
        for jsonfile in json_files:
            benchmark = json.load(open(jsonfile, "r"))
            for i in range(len(benchmark)):
                if "_Cmd" in benchmark[i]:
                    cmd_string = benchmark[i]["_Cmd"]
                    if cmd_string not in seen_cmds:
                        seen_cmds.append(cmd_string)
                        config_values["cmd"] += "\n" + cmd_string
                        break

            config_found = False
            for i in range(len(benchmark)):
                if config_found:
                    break
                for key in benchmark[i]:
                    if "_CONFIG-" in key:
                        config_values["item"].append(
                            key.replace("_", "") + "=" + benchmark[i][key]
                        )
                        config_found = True
    except OSError:
        logger.error("unable to open json file")

    args = {
        "build": build,
        "build_url": squad_build_url(group, project, build),
        "base_build": base_build,
        "config": config,
        "doc": doc_link,
        "compare_kernel": {"info": config_values},
        "regression_output": regression,
        "complete_output": full_output,
    }
    return te.get_template(config.template + ".txt.jinja").render(**args)
