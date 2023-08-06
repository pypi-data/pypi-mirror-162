""" GraphQL Helper Objects """
from enum import Enum
from typing import Any, Generic, NamedTuple, TypeVar

GraphQLVariableName = str
GraphQLVariableDataName = str

# pylint: disable-next=invalid-name
T = TypeVar('T')


class GraphQLVariableType(Enum):
    STRING_REQUIRED = 'String!'
    STRING_OPTIONAL = 'String'
    CREATE_RUN_INPUT = 'CreateRunInput!'
    GET_RUNS_INPUT = 'GetRunsInput!'


class GraphQLQueryVariable(NamedTuple):
    variableName: GraphQLVariableName
    variableDataName: GraphQLVariableDataName
    variableType: GraphQLVariableType


class FutureType(Generic[T]):
    """Typing for a `concurrent.futures.Future` response wrapper
    """

    def result(self, timeout: float) -> T:  # pylint: disable=unused-argument
        ...

    def set_exception(self, exc_info: BaseException):  # pylint: disable=unused-argument
        ...

    def set_result(self, result: Any):  # pylint: disable=unused-argument
        ...
