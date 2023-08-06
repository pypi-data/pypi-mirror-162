""" MCLI Abstraction for Platforms """
from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, Union

from mcli.utils.utils_kube import KubeContext, use_context
from mcli.utils.utils_serializable_dataclass import SerializableDataclass

logger = logging.getLogger(__name__)


class PlatformKubernetesError(Exception):
    """Error in platform kubernetes conversion """


@dataclass
class MCLIPlatform(SerializableDataclass):
    """Configured MCLI platform relating to specific kubernetes context
    """
    name: str
    kubernetes_context: str
    namespace: str

    @classmethod
    @contextmanager
    def use(cls, platform: Union[MCLIPlatform, str]) -> Generator[MCLIPlatform, None, None]:
        """Temporarily set the platform to use for all Kubernetes API calls

        Args:
            platform (MCLIPlatform): The platform to use

        Yields:
            MCLIPlatform: The provided platform
        """
        if isinstance(platform, str):
            mcli_platform = cls.get_by_name(platform)
        else:
            mcli_platform = platform

        with use_context(mcli_platform.kubernetes_context):
            yield mcli_platform

    def to_kube_context(self) -> KubeContext:
        """Get the corresponding KubeContext for this platform

        Returns:
            KubeContext with platform details
        """
        return KubeContext(name=self.kubernetes_context, namespace=self.namespace)

    @classmethod
    def from_kube_context(cls, context: KubeContext, platform_name: str) -> MCLIPlatform:
        """Create an MCLIPlatform from a KubeContext object

        Args:
            context: KubeContext containing platform details

        Returns:
            Platform with context details
        """
        if context.namespace is None:
            raise RuntimeError('Context must have a declared namespace')

        return cls(name=platform_name, kubernetes_context=context.name, namespace=context.namespace)

    @staticmethod
    def get_by_name(platform_name: str) -> MCLIPlatform:
        """Get a platform from the user's config by its name

        Args:
            platform_name: Name of the platform

        Raises:
            KeyError: Raised if the requested platform does not exist

        Returns:
            The requested platform
        """
        # pylint: disable-next=import-outside-toplevel
        from mcli.config import MCLIConfig

        conf = MCLIConfig.load_config(safe=True)
        for platform in conf.platforms:
            if platform.name == platform_name:
                return platform

        names = ', '.join(sorted([pl.name for pl in conf.platforms]))
        raise KeyError(f'Nonexistent platform: No platform named {platform_name}. Valid names are: {names}')
