from base64 import b64decode
import squad_report.logging
from squad_client.core.api import SquadApi

logger = squad_report.logging.getLogger(__name__)


def get_single_test_data(build, environment, suite):
    SquadApi.configure(url="https://qa-reports.linaro.org/")

    filters = {"environment__slug": environment, "metadata__suite": suite}

    build_metrics = {m.name: m.result for m in build.metrics(**filters).values()}

    if not build_metrics:
        raise ValueError(f"Data not found for {suite} on {environment}")

    result = {}
    first_module_name = None
    module_name = None
    operation = None
    cmd_pieces = {}

    for key, val in build_metrics.items():
        job_data = key.split("/")[1].split("_")

        if not first_module_name:
            first_module_name = job_data[0]
        module_name = job_data[0]

        if module_name not in result:
            result[module_name] = {
                "_ResultData": {},
                "_TestName": module_name,
                "_ModuleName": "Extract" + module_name.capitalize(),
                "_Cmd": "",
            }

        operation = str(job_data[1])
        iteration = int(job_data[2])
        sample = str(job_data[3])

        if operation == "#Cmd":
            if module_name not in cmd_pieces:
                cmd_pieces[module_name] = [{"pos": iteration, "text": sample}]
            else:
                cmd_pieces[module_name].append({"pos": iteration, "text": sample})
        elif "#CONFIG-" in operation:
            result[module_name][operation.replace("#", "_")] = sample
        else:
            if operation not in result[module_name]["_ResultData"]:
                result[module_name]["_ResultData"][operation] = []

                operation_length = len(result[module_name]["_ResultData"][operation])
                if operation_length <= iteration:
                    appends_to_do = (iteration + 1) - operation_length

                    for i in range(appends_to_do):
                        result[module_name]["_ResultData"][operation].append(
                            {"SampleNrs": [], "Values": []}
                        )

            result[module_name]["_ResultData"][operation][iteration][
                "SampleNrs"
            ].append(sample)
            result[module_name]["_ResultData"][operation][iteration]["Values"].append(
                val
            )

    for key, pieces in cmd_pieces.items():
        pieces.sort(key=lambda x: x["pos"])

        b64string = ""
        counter = -1
        for piece in pieces:
            if piece["pos"] > counter:
                counter = piece["pos"]
                b64string += piece["text"]

        # cmd string comes with no padding, add if needed
        missing_padding = len(b64string) % 4
        if missing_padding:
            b64string += "=" * (4 - missing_padding)

        try:
            decoded_string = b64decode(b64string).decode("utf-8")
        except Exception as e:
            logger.error(e)
            decoded_string = ""

        result[key]["_Cmd"] = decoded_string

    return result


def get_data(base_build, build, environment, suite):

    dict_data = {}

    try:
        data_base = get_single_test_data(base_build, environment, suite)
        data_current = get_single_test_data(build, environment, suite)
    except ValueError as e:
        logger.error(e)
        return

    for key in data_base:
        item = [data_base[key], data_current[key]]
        item[0]["_TestName"] = getattr(base_build, "version")
        item[1]["_TestName"] = getattr(build, "version")
        dict_data[key] = item

    return dict_data
