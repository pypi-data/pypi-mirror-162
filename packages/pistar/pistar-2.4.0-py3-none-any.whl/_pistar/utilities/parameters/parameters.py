"""
description: this module provides the function for parameters
"""
import enum
import itertools
import attr
import inspect
import functools
from _pistar.terminal import TerminalWriter
from typing import List, Union, Tuple, Sequence, Callable
from _pistar.utilities.testcase.exception import dedent, ExcInfoFormatter, ExceptionInfo
from _pistar.utilities.testcase.repr import LocationRepr, BaseRepr, ItemRepr


class Algorithm(enum.Enum):
    NONE = -1
    Full_Combination = 1

    @classmethod
    def __missing__(cls, key) -> "Algorithm":
        return Algorithm.NONE


def parameters(
    arg_names: Union[str, Sequence[str]],
    arg_values: Union[List, Tuple],
    *,
    indirect: bool = False,
    algorithm=Algorithm.NONE,
):
    """
    description: decorate of parameters, parse actual teststep arguments
                 and run the step
    arguments:
        arg_names:
            description: teststep parameter names
            type: str, list, tuple
        arg_values:
            description: teststep parameter values
            type: list, tuple
        indirect:
            description: whether to use condition, true if so
            type: bool
            default: false
        algorithm:
            description: built-in algorithm, users can expand more parameters
            type: Algorithm
            default: none
    return:
        type: Parameters
    """
    parameters_obj = Parameters(
        arg_names=arg_names,
        arg_values=arg_values,
        indirect=indirect,
        algorithm=algorithm,
    )
    return parameters_obj


class Parameters:
    """
    description: parameters decorate class, generate schedule strategy based on
                 testcase class
    attribute:
        arg_names:
            description: teststep parameter names
            type: str, list, tuple
        arg_values:
            description: teststep parameter values
            type: list, tuple
        indirect:
            description: whether to use condition, true if so
            type: bool
            default: false
        algorithm:
            description: built-in algorithm, users can expand more parameters
            type: Algorithm
            default: none
    """

    arg_names = None
    arg_values = None
    indirect = False
    algorithm = Algorithm.NONE
    parameters = list()

    def __init__(
        self, arg_names, arg_values, *, indirect=False, algorithm=Algorithm.NONE
    ):
        self.arg_names = arg_names
        self.arg_values = arg_values
        self.indirect = indirect
        self.algorithm = algorithm

        if not isinstance(self.arg_names, (str, list, tuple)):
            msg = (
                f"the type of argument arg_names '{self.arg_names}' is '{self.arg_names.__class__.__name__}', "
                f"but the 'str', 'list' or 'tuple' is expected"
            )
            raise TypeError(msg)
        if not isinstance(self.arg_values, (list, tuple)):
            msg = (
                f"the type of argument arg_values '{self.arg_values}' is '{self.arg_values.__class__.__name__}', "
                f"but the 'list' or 'tuple' is expected"
            )
            raise TypeError(msg)

        if not isinstance(self.indirect, bool):
            msg = (
                f"the type of argument indirect '{self.indirect}' is '{self.indirect.__class__.__name__}', "
                f"but the 'bool' is expected"
            )
            raise TypeError(msg)

        if self.indirect:
            self.parameters = [{}]
        else:
            self.arg_values = self.__transform_values()
            if isinstance(self.arg_names, str):
                self.parameters = [{self.arg_names: value} for value in self.arg_values]
            else:
                self.parameters = [
                    dict(zip(self.arg_names, value)) for value in self.arg_values
                ]

    def __transform_values(self):
        if self.algorithm == Algorithm.Full_Combination:
            return itertools.product(*self.arg_values)
        elif self.algorithm == Algorithm.NONE:
            return self.arg_values
        else:
            return self.arg_values

    def __execute(self, function, testcase, **kwargs):
        function.exec_result = dict(failed_params=list(), failed_params_count=0,
                                    passed_params_count=0, item_repr_list=list())
        for parameter in self.parameters:
            # For report printing specific parameters
            function.cur_param = [
                k + "=" + str(parameter.get(k, "")) for k in parameter
            ]
            try:
                function(testcase, **parameter, **kwargs)
                function.exec_result["passed_params_count"] += 1
            except Exception:
                function.exec_result["failed_params_count"] += 1
                function.exec_result["failed_params"].append(function.cur_param)
                exc_info = ExceptionInfo.from_current()
                fmt = ExcInfoFormatter(exc_info=exc_info, func=function)
                item_repr = fmt.repr_item_repr_exception()
                function.exec_result["item_repr_list"].append(item_repr)
        if function.exec_result["item_repr_list"]:
            raise ParametersLinkLookupError(function.exec_result)

    def __call__(self, function, **kwargs):
        @functools.wraps(function, **kwargs)
        def wrapper(*args, **kwargs):
            testcase = args[0]
            self.__execute(function, testcase, **kwargs)

        wrapper.param_arg_names = self.arg_names
        wrapper.parameters = self.parameters
        wrapper.indirect = self.indirect
        return wrapper


class ParametersLinkLookupError(LookupError):
    def __init__(self, param_exec_result: dict):
        super().__init__()
        self.param_exec_result = param_exec_result
        self.item_repr_list = self.param_exec_result.get("item_repr_list", list)
        self.failed_params = self.param_exec_result.get("failed_params", list)
        self.failed_params_count = self.param_exec_result.get("failed_params_count", list)
        self.passed_params_count = self.param_exec_result.get("passed_params_count", list)

    def format_repr(self) -> "ParametersLinkLookUpRepr":
        return ParametersLinkLookUpRepr(self.item_repr_list, self.failed_params,
                                        self.failed_params_count, self.passed_params_count)


@attr.s(eq=False, auto_attribs=True)
class ParametersLinkLookUpRepr(BaseRepr):
    item_repr_list: List[ItemRepr]
    failed_params: list
    failed_params_count: int
    passed_params_count: int

    def gen_repr(self, writer: TerminalWriter):
        # set the length of the separator according to the usual 80 characters per line in the Python specification
        delimiter_length = 80
        for index, item_repr in enumerate(self.item_repr_list):
            writer.line(">" * delimiter_length)
            item_repr.gen_repr(writer)
            writer.line("")
            writer.line("P   current parameters: " + " ".join(self.failed_params[index]))
            writer.line("<" * delimiter_length)
            writer.line("")
        writer.line("R" + "   parameters passed count:" + str(self.passed_params_count) +
                    ", failed count:" + str(self.failed_params_count))


class ParametersLookUpError(LookupError):
    """parameters args invalid."""

    def __init__(self, name: str, step: Callable, value: str = None):
        super().__init__()
        self.name = name
        self.value = value
        self.call = step

    def format_repr(self) -> "ParametersLookUpRepr":
        trace_line: List[str] = list()
        real_call = inspect.unwrap(self.call)
        fspath = inspect.getfile(real_call)
        sources, lineno = inspect.findsource(real_call)
        lines = dedent([line.rstrip() for line in sources])

        for line in lines[lineno:]:
            trace_line.append(f"{line.rstrip()}")
            if line.lstrip().startswith("def"):
                break

        msg = f"parameters '{self.name}' not found "
        if self.value:
            msg += f"in this set of parameters value: '{self.value}' "

        location = LocationRepr(path=fspath, lineno=lineno + 1, exception="")
        return ParametersLookUpRepr(location, msg=msg, lines=trace_line)


@attr.s(eq=False, auto_attribs=True)
class ParametersLookUpRepr(BaseRepr):
    location: "LocationRepr"
    msg: str
    lines: List[str]

    def gen_repr(self, writer: TerminalWriter):
        self.location.gen_repr(writer)
        for line in self.lines:
            writer.line(line.rstrip())

        writer.line(f"{ExcInfoFormatter.error_marker}      {self.msg.strip()}")
