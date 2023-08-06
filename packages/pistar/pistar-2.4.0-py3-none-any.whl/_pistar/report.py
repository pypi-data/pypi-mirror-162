from typing import Optional

from _pistar.caller import ExecuteInfo
from _pistar.config.cmdline import hookimpl
from _pistar.result import Result
from _pistar.utilities.exceptions.testcase import PassedException
from _pistar.utilities.testcase.case import TestCase
from _pistar.utilities.testcase.steps import Step
from _pistar.utilities.constants.testcase import TESTCASE_EXECUTION_STATUS


@hookimpl(hookwrapper=True)
def pistar_make_report(case: TestCase, call_info: ExecuteInfo, step: Step):
    result: Result = (yield).get_result()
    status_code = TESTCASE_EXECUTION_STATUS.PASSED if result.passed else \
        TESTCASE_EXECUTION_STATUS.FAILED
    exception = None
    if result.exception and not isinstance(result.exception, PassedException):
        exception = {
            "title": call_info.exc_info.exc_only(),
            "detail": result.longrepr
        }
    case.execute_records[step.name] = {
        "before": step.condition_result_cache,
        "start_time": call_info.begin,
        "end_time": call_info.end,
        "status_code": status_code,
        "exception": exception
    }
