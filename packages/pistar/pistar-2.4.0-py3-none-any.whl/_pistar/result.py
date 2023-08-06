import inspect
from typing import Optional, TYPE_CHECKING, Callable

from _pistar.caller import ExecuteInfo
from _pistar.config.cmdline import hookimpl
from _pistar.utilities.condition.condition import ConditionLookUpError
from _pistar.utilities.parameters.parameters import ParametersLookUpError
from _pistar.utilities.parameters.parameters import ParametersLinkLookupError
from _pistar.utilities.testcase.exception import ExceptionInfo, ExcInfoFormatter
from _pistar.utilities.testcase.steps import Step, TimeoutLookUpError
from _pistar.utilities.exceptions.testcase import TestCaseStatusException
from _pistar.utilities.testcase.case import TestCase
from _pistar.utilities.constants.testcase import \
    PISTAR_TESTCASE_EXECUTION_STATUS as STATUS, ControlArgs
from _pistar.utilities.constants.testcase import TESTCASE_EXECUTION_STATUS
from _pistar.utilities.testcase.repr import BaseRepr

if TYPE_CHECKING:
    from typing_extensions import Literal


def set_status_by_call(call: ExecuteInfo):
    if call.exc_info:
        if call.when == "init":
            return STATUS.ERROR
        elif isinstance(call.exc_info.value, TestCaseStatusException):
            return call.exc_info.value.value
        else:
            return STATUS.FAILED
    return STATUS.PASSED


def format_repr_info(exc_repr):
    if isinstance(exc_repr, list):
        format_repr = "\n".join([str(per_exc_repr) for per_exc_repr in exc_repr])
    else:
        format_repr = str(exc_repr)
    return format_repr


def get_exception_repr(exc_info: ExceptionInfo, func: Callable) -> str:
    """
    description: Format the complete exception information to get the
    pure exception information on the script side
    """
    fmt = ExcInfoFormatter(exc_info=exc_info, func=func)
    if isinstance(exc_info.value, (ConditionLookUpError, ParametersLookUpError,
                                   TimeoutLookUpError, ParametersLinkLookupError)):
        exc_repr = exc_info.value.format_repr()
    else:
        exc_repr = fmt.repr_impl_exception()
    return format_repr_info(exc_repr)


def set_exception_from_call(call: ExecuteInfo):
    if not call.exc_info:
        return None
    else:
        return call.exc_info.value


class Result:
    def __init__(self,
                 node_id: str,
                 status: int,
                 duration: float,
                 exception: Optional[BaseException],
                 longrepr: Optional[BaseRepr],
                 when: "Literal['collect', 'init', 'setup', 'call', 'teardown']"):
        self.node_id = node_id
        self.status = status
        self.duration = duration
        self.exception = exception
        self.longrepr = longrepr
        self.when = when

    @classmethod
    def from_call_and_step(cls, case: TestCase, call: ExecuteInfo, step: Optional[Step] = None):
        exception = set_exception_from_call(call)
        longrepr = cls.get_repr_from_args(case, call, step)
        status = set_status_by_call(call)

        return cls(
            case.nodeid,
            status,
            call.duration,
            exception,
            longrepr,
            call.when
        )

    @staticmethod
    def get_repr_from_args(case: TestCase, call: ExecuteInfo, step: Optional[Step] = None):
        if not call.exc_info:
            longrepr = None
        else:
            if call.when == "init":
                func = case.clazz.__init__
            elif call.when == "setup":
                func = case.setup
            elif call.when == "call":
                func = step.stepobj
            elif case.execution_status == STATUS.PASSED:
                func = case.teardown
            else:
                func = case.failure
            longrepr = get_exception_repr(exc_info=call.exc_info, func=inspect.unwrap(func))
        return longrepr

    @property
    def passed(self):
        return self.status == STATUS.PASSED

    @property
    def failed(self):
        return self.status != STATUS.PASSED


@hookimpl
def pistar_make_report(case: TestCase, call_info: ExecuteInfo, step: Optional[Step]) \
        -> Result:
    """
    this function is used to return a result of the executed step.
    """
    result = Result.from_call_and_step(case=case, call=call_info, step=step)
    if result.failed:
        case.execution_status = TESTCASE_EXECUTION_STATUS.FAILED
        case.execution_exceptions.append(result.longrepr)

    control_status = getattr(case.instance, ControlArgs.RIGOROUS, None)
    if hasattr(step.stepobj, "start") and control_status is False:
        step.stepobj.end.value = True
    return result
