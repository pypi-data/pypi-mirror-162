import json
import os
from typing import Dict

from _pistar.pistar_pytest.utils import now
from _pistar.utilities.constants.encode import ENCODE
from _pistar.utilities.constants.file_mode import FILE_MODE
from _pistar.utilities.constants.testcase import PISTAR_TESTCASE_EXECUTION_STATUS as \
    PISTAR_STATUS
from _pistar.utilities.testcase.case import TestCase
from _pistar.utilities.report.pistar_report_info import PistarReportInfo
from _pistar.agent import generate_finish_file


def get_report_info(testcase: TestCase):
    """
    description: get report data by report_type
    parameter:
        report_type:
            description: the report_type
            type:str
    return:
        report
    """
    report_info = PistarReportInfo(testcase)

    return report_info


def generate_report_file(testcase, report_info):
    output_path = testcase.clazz.testcase_result_path
    for teststep in report_info.get("details"):
        report_json_file = "".join([teststep.get("name", ""), "-result.json"])
        with open(os.path.join(output_path, report_json_file), mode=FILE_MODE.WRITE, encoding=ENCODE.UTF8) as file:
            json.dump(teststep, file, ensure_ascii=False, default=str)


def generate_report_and_finish_file(case: TestCase, report_info: PistarReportInfo) -> Dict[str, int]:
    if report_info["details"]:
        status = PISTAR_STATUS.PASSED if case.execution_status == "0" else PISTAR_STATUS.FAILED
        start_time = case.start_time
        if case.is_timeout:
            end_time = now()
            exception_info = "TimeoutError"
        else:
            end_time = case.end_time
            exception_info = None if status == PISTAR_STATUS.PASSED else \
                str(case.execution_exceptions[-1])
    else:
        status = PISTAR_STATUS.ERROR
        start_time = now()
        end_time = start_time
        exception_info = case.exception["detail"]
    generate_report_file(case, report_info)
    generate_finish_file(
        output_dir=str(case.clazz.testcase_result_path),
        start_time=start_time,
        end_time=end_time,
        status=status,
        attach_path=str(case.clazz.logger_path),
        exception_info=exception_info
    )
    return {"::".join([case.path, case.name]): status}
