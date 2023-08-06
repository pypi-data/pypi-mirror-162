"""Cloud exceptions thrown"""
from __future__ import annotations

import functools
import logging
from enum import Enum
from http import HTTPStatus
from typing import Any, Callable, Optional, Type, TypeVar, Union

from kubernetes.client.exceptions import ApiException

logger = logging.getLogger(__name__)


class MAPIException(Exception):
    """Exceptions raised when a request to MAPI fails

    Args:
        status: The status code for the exception
        message: A brief description of the error
        description: An optional longer description of the error

    Details:
    MAPI responds to failures with the following status codes:
    - 400: The request was misconfigured or missing an argument. Double-check the API and try again
    - 401: User credentials were either missing or invalid. Be sure to set your API key before making a request
    - 403: User credentials were valid, but the requested action is not allowed
    - 404: Could not find the requested resource(s)
    - 409: Attempted to create an object with a name that already exists. Change the name and try again.
    - 500: Internal error in MAPI. Please report the issue
    - 503: MAPI or a subcomponent is currently offline. Please report the issue
    """
    status: HTTPStatus
    message: str
    description: Optional[str] = None

    def __init__(self, status: HTTPStatus, message: str, description: Optional[str] = None):
        super().__init__()
        self.status = status
        self.message = message
        self.description = description

    def __str__(self) -> str:
        error_message = f'Error {self.status.value}: {self.message}'

        if self.description:
            error_message = f'{error_message}. {self.description}'

        return error_message


class KubernetesErrorDesc(Enum):
    """Provides descriptions for common Kubernetes errors that we might encounter
    """

    UNAUTHORIZED = 'Invalid cluster credentials: Please contact your cluster administrator'
    FORBIDDEN = 'Invalid permissions: The requested action is not allowed. Please contact your cluster administrator'
    CONFLICT = 'Object already exists: Please ensure you are using unique names'
    UNPROCESSABLE_ENTITY = ('Submitted object misconfigured: This usually occurs when secrets and other objects '
                            'are duplicated. Please double-check and try again.')
    INTERNAL_SERVER_ERROR = ('Cluster error: The cluster seems to be struggling with something. '
                             'Please report this issue to your cluster administrator')


TFunc = TypeVar('TFunc', bound=Callable[..., Any])


class KubernetesException(MAPIException):
    """Exceptions raised when a Kubernetes request fails

    Args:
        status: The status code for the exception
        message: A brief description of the error
        description: An optional longer description of the error

    Details:
    Kubernetes will respond with a variety of status codes when a request fails. Below are some of the common ones:
    - 401: User credentials were invalid. Check with your cluster administrator on how to get new ones
    - 403: User credentials were valid, but the requested action is not allowed
    - 409: Attempted to create an object with a name that already exists. Change the name and try again.
    - 422: Submitted object misconfigured: This usually occurs when secrets and other objects
           are duplicated. Please double-check and try again.
    - 500: Internal cluster error. Please report the issue
    """

    @classmethod
    def transform_api_exception(
        cls: Type[KubernetesException],
        e: ApiException,
    ) -> Union[KubernetesException, ApiException]:

        try:
            status = HTTPStatus(e.status)
            message = KubernetesErrorDesc[status.name].value  # pylint: disable=no-member
        except (KeyError, TypeError):
            return e

        logger.debug(f'Transformed Kubernetes exception: {e}')
        return cls(status=status, message=message)

    @classmethod
    def wrap(cls, f: TFunc) -> TFunc:
        """Wrap the provided callable to catch any Kubernetes ApiException and
        throw a transformed KubernetesException

        Args:
            f: Callable that might raise an ApiException

        Raises:
            KubernetesException: Raised if an ApiException was hit that we know how to message to the user
            ApiException: Raised if an unfamiliar ApiException is hit

        Returns:
            A wrapped callable
        """

        @functools.wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            try:
                return f(*args, **kwargs)
            except ApiException as e:
                raise cls.transform_api_exception(e) from e

        return wrapped  # type: ignore
