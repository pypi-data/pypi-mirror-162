""" GraphQL Query Engine """
from __future__ import annotations

import json
from concurrent.futures import Future, ThreadPoolExecutor
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import requests

from mcli.api.exceptions import KubernetesException, MAPIException
from mcli.api.schema.query_models import SuccessResponse, T_DeserializableModel, UnserializedSuccessResponse

__all__ = [
    'MAPIConnection',
    'run_graphql_success_query',
]

# pylint: disable-next=invalid-name
THREADPOOL_WORKERS = 10
THREADPOOL: Optional[ThreadPoolExecutor] = None


def _create_threadpool() -> ThreadPoolExecutor:
    """Create a global threadpool for requests
    """
    global THREADPOOL
    THREADPOOL = ThreadPoolExecutor(max_workers=THREADPOOL_WORKERS, thread_name_prefix='mosaicml-api')
    return THREADPOOL


class MAPIConnection:
    """Connection to a user's MAPI instance

    Args:
        api_key: The user's API key. If not specified, the value of the $MOSAICML_API_KEY
            environment variable will be used. If that does not exist, the value in the
            user's config file will be used. If that does not exist, a MAPIException will
            be thrown.
        endpoint: The MAPI URL to hit for all requests. If not specified, the value of the
            $MOSAICML_API_ENDPOINT environment variable will be used. If that does not
            exist, the default setting will be used.
        pool: An optional threadpool to use for all connection requests. If not provided,
            a shared pool will be used for all requests.

    Raises:
        MAPIException: Raised if the user does not have an API key set
    """
    api_key: str
    endpoint: str

    def __init__(self,
                 api_key: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 pool: Optional[ThreadPoolExecutor] = None):
        self._load_from_environment(api_key, endpoint)
        self._pool = pool
        self._prev: Optional[MAPIConnection] = None

    def _load_from_environment(self, api_key: Optional[str] = None, endpoint: Optional[str] = None) -> None:
        # pylint: disable-next=import-outside-top-level
        from mcli import config

        if api_key is None:
            api_key = config.MCLIConfig().load_config().MOSAICML_API_KEY

        if api_key is None:
            raise MAPIException(
                status=HTTPStatus.UNAUTHORIZED,
                message=('User does not have an API key set. Please set the environment variable $MOSAICML_API_KEY '
                         'to connect to the MosaicML cloud'),
            )
        self.api_key = api_key

        if endpoint is None:
            config.env_str_override_config('MOSAICML_API_ENDPOINT')
            endpoint = config.MOSAICML_API_ENDPOINT
        self.endpoint = endpoint

    @staticmethod
    def _set_connection(connection: Optional[MAPIConnection]) -> None:
        """Set the current connection instance

        Args:
            connection: The desired connection instance
        """
        global _CONNECTION
        _CONNECTION = connection

    @property
    def pool(self) -> ThreadPoolExecutor:
        """The ThreadPoolExecutor that will contain all MAPI requests
        """
        if self._pool is None:
            self._pool = THREADPOOL or _create_threadpool()

        return self._pool

    @staticmethod
    def get_current_connection() -> MAPIConnection:
        """Get the current connection instance
        """
        return _CONNECTION or _create_default_connection()

    def __enter__(self) -> MAPIConnection:
        self._prev = _CONNECTION
        self._set_connection(self)
        return self

    def __exit__(self, type_, value, traceback):
        self._set_connection(self._prev)


_CONNECTION: Optional[MAPIConnection] = None


def _create_default_connection() -> MAPIConnection:
    """Creates the default MAPIConnection object
    """
    global _CONNECTION
    _CONNECTION = MAPIConnection()
    return _CONNECTION


# pylint: disable-next=invalid-name
T_ModelOrList = Optional[Union[T_DeserializableModel, List[T_DeserializableModel]]]
TFunc = TypeVar('TFunc', bound=Callable[..., T_ModelOrList])


# TODO: Figure out proper typing of this
def async_kubernetes_calls(
    f: TFunc,
    *args: Any,
    connection: Optional[MAPIConnection] = None,
    **kwargs: Any,
) -> Future[T_ModelOrList]:
    """Wrap a function that calls Kubernetes and returns a :type DeserializableModel: in
    a Future

    Args:
        f: Function that calls Kubernetes
        *args, **kwargs: Arbitrary arguments with which to call ``f``
        connection: Optional :type MAPIConnection: whose threadpool will be used

    Returns:
        A Future for the return value of ``f``
    """
    if not connection:
        connection = MAPIConnection.get_current_connection()
    return connection.pool.submit(KubernetesException.wrap(f), *args, **kwargs)


def run_graphql_success_query(
    query: str,
    query_function: str,
    return_model_type: Optional[Type[T_DeserializableModel]] = None,
    variables: Optional[Dict[str, Any]] = None,
    connection: Optional[MAPIConnection] = None,
) -> Future[T_ModelOrList]:
    """Run a GraphQL query against MAPI

    Args:
        query: Query to run
        query_function: GraphQL endpoint for the query (e.g. 'createRun')
        return_model_type: The data type into which the response should be deserialized.
            Required if data is expected to be returned.
        variables: Variables to be passed to the GraphQL endpoint. Defaults to None.
        connection: The MAPI connection that should be used. Defaults to the connection
            returned by `MAPIConnection.get_current_connection()`.

    Returns:
        A `concurrent.futures.Future` for the request. You can retrieve the data using
        `future.result()` with an optional `timeout` argument.
    """
    if not connection:
        connection = MAPIConnection.get_current_connection()

    future = connection.pool.submit(
        _threaded_graphql_request,
        api_key=connection.api_key,
        endpoint=connection.endpoint,
        query=query,
        variables=variables,
        query_function=query_function,
        model_type=return_model_type,
    )

    return future


def _threaded_graphql_request(
    api_key: str,
    endpoint: str,
    query: str,
    variables: Optional[Dict[str, Any]],
    query_function: str,
    model_type: Optional[Type[T_DeserializableModel]],
) -> T_ModelOrList:
    """Run a graphql request in a thread

    Args:
        api_key: API key to use for the request
        endpoint: Endpoint to hit for the request
        query: Request query
        variables: Request variables
        query_function: Query function name
        model_type: Type of model to deserialize

    Returns:
        The deserialized response, a list of deserialized response objects, or None if no
        data was returned from the request

    Raises:
        MAPIException: Raised if the request fails. See ``MAPIException`` for details on
        exception status codes
    """
    response = _run_graphql_request(api_key, endpoint, query, variables)
    deserialized = _deserialize_response(response, query_function, model_type)

    if deserialized.item is not None:
        return deserialized.item
    elif deserialized.items is not None:
        return deserialized.items
    else:
        return None


def _run_graphql_request(
    api_key: str,
    endpoint: str,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    if variables is None:
        variables = {}
    variables = {key.replace('$', ''): value for key, value in variables.items()}

    headers = {
        'Content-Type': 'application/json',
        'authorization': api_key,
    }
    payload = json.dumps({'query': query, 'variables': variables})
    response = requests.request(
        'POST',
        endpoint,
        headers=headers,
        data=payload,
    )
    return response.json()


def _deserialize_response(
    response: Dict[str, Any],
    query_function: str,
    model_type: Optional[Type[T_DeserializableModel]],
) -> SuccessResponse[T_DeserializableModel]:

    try:
        data = response['data']
        query_response: Dict[str, Any] = data[query_function]
        query_response['model_type'] = model_type
        raw_response = UnserializedSuccessResponse(**query_response)
        if not raw_response.success:
            # TODO: Properly handle failed responses
            raise MAPIException(
                HTTPStatus.BAD_REQUEST,
                message=raw_response.message or 'Unknown error',
                description=raw_response.messageLong,
            )
        return raw_response.deserialize()
    except KeyError:
        # TODO: Remove when proper 401 errors are thrown
        # Currently a request without an API key set return a response without 'data'
        raise MAPIException(HTTPStatus.UNAUTHORIZED, 'API key not set or invalid')

    except Exception as e:  # pylint: disable=broad-except
        # TODO: Remove this when MAPI response errors are clear
        if 'errors' in response:
            error_message = ''
            for error in response['errors']:
                error_message += error['message'] + '\n'
            if error_message == '':
                error_message = 'Unknown GraphQL Error Message'
            raise Exception(f'GraphQL Exception:\n\n{error_message}') from e
        else:
            print(f'Failed to run query: {query_function}')
            raise e
