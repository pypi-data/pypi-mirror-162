from typing import Optional, TYPE_CHECKING, Dict

from _pistar.caller import ExecuteInfo
from _pistar.utilities.testcase.steps import Step
from _pistar.utilities.exceptions.testcase import PassedException
from _pistar.config.cmdline import hookimpl
from _pistar.utilities.constants.testcase import TESTCASE_EXECUTION_STATUS


if TYPE_CHECKING:
    from _pistar.result import Result
    from _pistar.utilities.testcase.case import TestCase


def set_execution_log(case: "TestCase", msg):
    case.clazz.info(msg)


@hookimpl(hookwrapper=True)
def pistar_make_report(case: "TestCase", call_info: ExecuteInfo, step: Optional[Step]):
    result: "Result" = (yield).get_result()
    if result.passed and isinstance(result.exception, PassedException):
        case.clazz.info(str(result.exception))
    elif result.longrepr and result.failed:
        case.clazz.error(result.longrepr)
    status = "passed" if result.passed else "failed"
    set_execution_log(case, msg=f"step {step.name} end, result: {status}")


@hookimpl(tryfirst=True)
def pistar_step_call(step: Step):
    set_execution_log(step.parent, f"step {step.name} start.")
    if step.stepobj.description:
        set_execution_log(step.parent, f"step {step.name} description: {step.stepobj.description}")


@hookimpl(tryfirst=True)
def pistar_run_log_end(case: "TestCase"):
    set_execution_log(case, msg=f"case {case.name} end.")
    result = "passed" if TESTCASE_EXECUTION_STATUS.PASSED == case.execution_status else "failed"
    set_execution_log(case, msg=f"case {case.name} result: {result}.")


@hookimpl(tryfirst=True)
def pistar_run_setup(step: Step):
    set_execution_log(step.parent, msg=f"step {step.name} start.")


@hookimpl(tryfirst=True)
def pistar_run_teardown(step: Step):
    set_execution_log(step.parent, msg=f"step {step.name} end.")


def log_for_exceptions(
        case: "TestCase",
        pure_traceback_exception: Dict[str, str]
) -> None:
    case.clazz.error(f'{pure_traceback_exception["detail"]}')
