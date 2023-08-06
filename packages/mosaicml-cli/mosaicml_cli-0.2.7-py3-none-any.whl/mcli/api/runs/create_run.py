""" Create a Run """
from __future__ import annotations

from concurrent.futures import Future
from typing import Optional, overload

from typing_extensions import Literal

from mcli.api.engine.engine import run_graphql_success_query
from mcli.api.model.run_model import RunModel, get_run_schema
from mcli.api.schema.query import named_success_query
from mcli.api.types import GraphQLQueryVariable, GraphQLVariableType
from mcli.models.run_input import RunInput


@overload
def create_run(run: RunInput, timeout: Optional[float] = 10, future: Literal[False] = False) -> RunModel:
    ...


@overload
def create_run(run: RunInput, timeout: Optional[float] = None, future: Literal[True] = True) -> Future[RunModel]:
    ...


def create_run(run: RunInput, timeout: Optional[float] = 10, future: bool = False):
    """Launch a run in the MosaicML Cloud

    The provided ``run`` must contain enough information to fully detail the run

    Args:
        run: A fully-configured run to launch. The run will be queued and persisted
            in the run database.
        timeout: Time, in seconds, in which the call should complete. If the run creation
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :type concurrent.futures.Future:. If True, the
            call to `create_run` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type RunModel: output, use ``return_value.result()``
            with an optional ``timeout`` argument.

    Returns:
        A RunModel that includes the launched run details and the run status
    """

    query_function = 'createRun'
    variable_data_name = '$createRunInput'
    variables = {
        variable_data_name: run.to_create_run_api_input(),
    }
    graphql_variable: GraphQLQueryVariable = GraphQLQueryVariable(
        variableName='createRunData',
        variableDataName=variable_data_name,
        variableType=GraphQLVariableType.CREATE_RUN_INPUT,
    )

    query = named_success_query(
        query_name='CreateRun',
        query_function=query_function,
        query_item=get_run_schema(),
        variables=[graphql_variable],
        is_mutation=True,
    )

    response = run_graphql_success_query(
        query=query,
        query_function=query_function,
        return_model_type=RunModel,
        variables=variables,
    )

    if not future:
        return response.result(timeout=timeout)
    else:
        return response
