""" Run Input """
from __future__ import annotations

import logging
import warnings
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcli.api.schema.generic_model import DeserializableModel
from mcli.serverside.platforms.platform_instances import (IncompleteInstanceRequest, InstanceRequest,
                                                          UserInstanceRegistry, ValidInstance)
from mcli.utils.utils_config import uuid_generator
from mcli.utils.utils_string_validation import ensure_rfc1123_compatibility, validate_rfc1123_name
from mcli.utils.utils_yaml import load_yaml

logger = logging.getLogger(__name__)
RUN_INPUT_UID_LENGTH = 4


@dataclass
class RunInput(DeserializableModel):
    """ Run Input """

    run_id: str
    run_name: str

    gpu_type: str
    gpu_num: int
    cpus: int

    platform: str
    image: str
    integrations: List[Dict[str, Any]]
    env_variables: List[Dict[str, str]]

    parameters: Dict[str, Any]

    # Make both optional for initial rollout
    # Eventually make entrypoint required and deprecate command
    command: str = ''
    entrypoint: str = ''

    property_translations = {
        'runUid': 'run_uid',
        'runName': 'run_name',
        'gpuType': 'gpu_type',
        'gpuNum': 'gpu_num',
        'cpus': 'cpus',
        'platform': 'platform',
        'image': 'image',
        'integrations': 'integrations',
        'envVariables': 'env_variables',
        'parameters': 'parameters',
        'command': 'command',
        'entrypoint': 'entrypoint',
    }

    @classmethod
    def from_partial_run_input(cls, partial_run_input: PartialRunInput) -> RunInput:
        """Create a RunInput from the provided PartialRunInput.

        If the PartialRunInput is not fully populated then this function fails with an error.

        Args:
            partial_run_input (PartialRunInput): The PartialRunInput

        Returns:
            RunInput: The RunInput object created using values from the PartialRunInput
        """

        if partial_run_input.cpus is None:
            partial_run_input.cpus = 0

        if not all((
                partial_run_input.platform,
                partial_run_input.gpu_type,
                partial_run_input.gpu_num is not None,
        )):
            # Try to infer values from provided
            request = InstanceRequest(platform=partial_run_input.platform,
                                      gpu_type=partial_run_input.gpu_type,
                                      gpu_num=partial_run_input.gpu_num)
            logger.debug(f'Incomplete instance request: {request}')
            user_instances = UserInstanceRegistry()
            options = user_instances.lookup(request)
            if len(options) == 1:
                valid_instance = options[0]
                logger.debug(f'Inferred a valid instance request: {valid_instance}')
                partial_run_input.platform = valid_instance.platform
                partial_run_input.gpu_type = valid_instance.gpu_type
                partial_run_input.gpu_num = valid_instance.gpu_num
            else:
                valid_registry = ValidInstance.to_registry(options)
                raise IncompleteInstanceRequest(
                    requested=request,
                    options=valid_registry,
                    registry=user_instances.registry,
                )

        model_as_dict = asdict(partial_run_input)
        missing_fields = [field for field, value in model_as_dict.items() if value is None]
        if len(missing_fields) > 0:
            logger.error(f'[ERROR] Cannot construct run because of missing fields {missing_fields}.'
                         ' Please pass the missing fields either in a yaml file or as command line arguments.')
            missing_fields_string = ', '.join(missing_fields)
            raise Exception(f'Cannot construct RunInput with missing fields: {missing_fields_string}')

        # Fill in default initial values for RunInput
        model_as_dict.update({
            'run_id': uuid_generator(RUN_INPUT_UID_LENGTH),
        })

        if model_as_dict.get('run_name', None):
            run_name = model_as_dict['run_name']
            name_validation = validate_rfc1123_name(text=run_name)
            if not name_validation.valid:
                warning_prefix = 'WARNING: '
                logger.warning(warning_prefix + f'Invalid RFC 1123 Name: {run_name}')
                # TODO: Figure out why logging strips out regex []
                # (This is a rich formatting thing. [] is used to style text)
                logger.warning((warning_prefix + str(name_validation.message)))
                logger.warning(warning_prefix + 'Converting run_name to be RFC 1123 Compliant')
                new_run_name = ensure_rfc1123_compatibility(run_name)
                model_as_dict['run_name'] = new_run_name
                logger.warning(warning_prefix + f'New run_name: {new_run_name}')

        if isinstance(model_as_dict.get('gpu_type'), int):
            model_as_dict['gpu_type'] = str(model_as_dict['gpu_type'])

        # Do not support specifying both a command and an entrypoint because the two might
        # conflict with each other
        if partial_run_input.command and partial_run_input.entrypoint:
            raise Exception('Specifying both a command and entrypoint as input is not supported.'
                            'Please only specify one of command or entrypoint.')

        if not (partial_run_input.command or partial_run_input.entrypoint):
            raise Exception('Must specify one of command or entrypoint as input.')

        return cls(**model_as_dict)

    def to_create_run_api_input(self):
        translations = {RunInput.property_translations[k]: k for k in RunInput.property_translations}

        translated_input = {}
        for field_name, value in asdict(self).items():
            translated_name = translations.get(field_name, field_name)
            translated_input[translated_name] = value

        return {
            'runInput': translated_input,
        }


@dataclass
class PartialRunInput:
    """ Partial Run Input """
    run_name: Optional[str] = None
    gpu_type: Optional[str] = None
    gpu_num: Optional[int] = None
    cpus: Optional[int] = None
    platform: Optional[str] = None
    image: Optional[str] = None
    integrations: List[Dict[str, Any]] = field(default_factory=list)
    env_variables: List[Dict[str, str]] = field(default_factory=list)

    command: str = ''
    parameters: Dict[str, Any] = field(default_factory=dict)
    entrypoint: str = ''

    @classmethod
    def empty(cls) -> PartialRunInput:
        return cls()

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> PartialRunInput:
        """Load the config from the provided YAML file.

        Args:
            path (Union[str, Path]): Path to YAML file

        Returns:
            PartialRunInput: The PartialRunInput object specified in the YAML file
        """
        config = load_yaml(path)
        return cls.from_dict(config, show_unused_warning=True)

    @classmethod
    def from_dict(cls, dict_to_use: Dict[str, Any], show_unused_warning: bool = False) -> PartialRunInput:
        """Load the config from the provided dictionary.

        Args:
            dict_to_use (Dict[str, Any]): The dictionary to populate the PartialRunInput with

        Returns:
            PartialRunInput: The PartialRunInput object specified in the dictionary
        """
        field_names = list(map(lambda x: x.name, fields(cls)))

        unused_keys = []
        constructor = {}
        for key, value in dict_to_use.items():
            if key in field_names:
                constructor[key] = value

            else:
                unused_keys.append(key)

        if len(unused_keys) > 0 and show_unused_warning:
            warnings.warn(f'Encountered fields {unused_keys} which were not used in constructing the run.')

        return cls(**constructor)
