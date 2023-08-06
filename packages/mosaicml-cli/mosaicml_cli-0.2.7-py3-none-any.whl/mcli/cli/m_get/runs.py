"""Implementation of mcli get runs"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Union

from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay
from mcli.config import MESSAGE, MCLIConfig, MCLIConfigError
from mcli.objects.platforms.platform_info import get_platform_list
from mcli.serverside.platforms import GPUType
from mcli.serverside.platforms.platform_instances import InstanceRequest, UserInstanceRegistry
from mcli.utils.utils_epilog import ContextPodStatus
from mcli.utils.utils_kube import group_pods_by_job, list_pods_across_contexts
from mcli.utils.utils_kube_labels import extract_label_values, label
from mcli.utils.utils_logging import FAIL, console
from mcli.utils.utils_pod_state import PodState

logger = logging.getLogger(__name__)


def to_camel_case(text: str):
    return text.title().replace('_', '')


def aggregate_statuses(pod_statuses: List[ContextPodStatus]) -> str:
    """Aggregate statuses across all pods for a run

    Arguments:
        pod_statuses: List of pod status tuples

    Returns:
        string form of the aggregated status

    NOTE: Returning string for now since, in the future, we may want to provide
    short-string feedback on individual pods in a run
    """
    return to_camel_case(ContextPodStatus.aggregate(pod_statuses).state.value)


class RunColumns(Enum):
    NAME = 'name'
    PLATFORM = 'platform'
    GPU_TYPE = 'gpu_type'
    GPU_NUM = 'gpu_num'
    CREATED_TIME = 'created_time'
    START_TIME = 'start_time'
    END_TIME = 'end_time'
    STATUS = 'status'


def format_datetime(timestamp: str) -> str:
    timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
    iso_date = dt.datetime.fromisoformat(timestamp).astimezone(timezone)
    return iso_date.strftime('%Y-%m-%d %I:%M %p')


def get_start_time(pod_dict: Dict[str, Any], default='-') -> str:
    # note: pod startTime not the container start time. Useful for
    # cost estimation and may be slightly less than container due
    # to the time needed to pull the image inside the container
    try:
        return format_datetime(pod_dict['status']['startTime'])
    except KeyError:
        return default


def get_end_time(pod_dict: Dict[str, Any], default='-') -> str:
    try:
        container_status = pod_dict['status']['containerStatuses'][0]
        terminated = container_status['state'].get('terminated')
        if not terminated:
            return default
        return format_datetime(terminated['finishedAt'])
    except (KeyError, IndexError):
        return default


@dataclass
class RunDisplayItem(MCLIDisplayItem):
    """Tuple that extracts run data for display purposes.
    """
    gpu_num: str
    created_time: str
    start_time: str
    end_time: str
    status: str
    platform: Optional[str] = None
    gpu_type: Optional[str] = None

    @classmethod
    def from_pod_group(cls, pod_group: List[Dict[str, Any]], use_compact_view: bool) -> RunDisplayItem:
        # There will always be at least one pod associated with a job
        pod = pod_group[0]
        pod_labels: Dict[str, str] = dict(pod['metadata'].get('labels', {}))
        labels_to_get = [
            label.mosaic.JOB, label.compute.LABEL_MCLI_PLATFORM, label.compute.LABEL_GPU_TYPE,
            label.compute.LABEL_GPU_NUM
        ]
        label_vals = extract_label_values(pod_labels, labels_to_get, default='-')

        extracted: Dict[str, str] = {RunColumns.NAME.value: label_vals[label.mosaic.JOB]}
        if not use_compact_view:
            extracted[RunColumns.PLATFORM.value] = label_vals[label.compute.LABEL_MCLI_PLATFORM]
            extracted[RunColumns.GPU_TYPE.value] = label_vals[label.compute.LABEL_GPU_TYPE]
        extracted[RunColumns.GPU_NUM.value] = label_vals[label.compute.LABEL_GPU_NUM]
        extracted[RunColumns.CREATED_TIME.value] = format_datetime(pod['metadata']['creationTimestamp'])
        extracted[RunColumns.START_TIME.value] = get_start_time(pod)
        extracted[RunColumns.END_TIME.value] = get_end_time(pod)

        pod_statuses = [ContextPodStatus.from_pod_dict(pod_dict) for pod_dict in pod_group]
        extracted[RunColumns.STATUS.value] = aggregate_statuses(pod_statuses)
        return cls(**extracted)


class MCLIRunDisplay(MCLIGetDisplay):
    """Display manager for runs
    """

    def __init__(self, pod_grouping_by_job: Dict[str, Any], status: Optional[str] = None):
        self.grouping = pod_grouping_by_job
        self.status = status

        # Each inner list is a group of pods associated with a job
        self.ordered_pod_groups: List[List[Dict[str,
                                                Any]]] = (sorted(self.grouping.values(),
                                                                 key=lambda x: x[0]['metadata']['creationTimestamp'],
                                                                 reverse=True))

        # Omit platform and gpu_type columns if there only exists one valid platform/gpu_type combination
        # available to the user
        self.use_compact_view = False
        platforms_list = get_platform_list()
        if len(platforms_list) == 1:
            request = InstanceRequest(platform=platforms_list[0].name, gpu_type=None, gpu_num=None)
            user_instances = UserInstanceRegistry()
            options = user_instances.lookup(request)
            num_gpu_types = len(set([x.gpu_type for x in options if GPUType.from_string(x.gpu_type) != GPUType.NONE]))
            if num_gpu_types <= 1:
                self.use_compact_view = True

    @property
    def override_column_ordering(self) -> Optional[List[str]]:
        if self.use_compact_view:
            return [
                RunColumns.GPU_NUM.value, RunColumns.CREATED_TIME.value, RunColumns.START_TIME.value,
                RunColumns.END_TIME.value, RunColumns.STATUS.value
            ]
        return [e.value for e in RunColumns][1:]  # exclude 'name' column

    def __iter__(self) -> Generator[RunDisplayItem, None, None]:
        for pod_group in self.ordered_pod_groups:
            item = RunDisplayItem.from_pod_group(pod_group, self.use_compact_view)
            if not self.status or item.status.lower() == self.status:
                yield item


def get_runs(platform: Optional[str] = None,
             gpu_type: Optional[str] = None,
             gpu_num: Optional[str] = None,
             status: Optional[str] = None,
             output: OutputDisplay = OutputDisplay.TABLE,
             **kwargs) -> int:
    """Get a table of ongoing and completed runs
    """
    del kwargs

    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1

    if not conf.platforms:
        logger.error(f'{FAIL} No platforms created. You must have at least one platform before you can get '
                     'runs. Please run `mcli create platform` to create your first platform.')
        return 1

    # Filter platforms
    if platform is not None:
        chosen_platforms = [p for p in conf.platforms if p.name == platform]
        if not chosen_platforms:
            platform_names = [p.name for p in conf.platforms]
            logger.error(f'{FAIL} Platform not found. Platform name should be one of {platform_names}, '
                         f'not "{platform}".')
            return 1
    else:
        chosen_platforms = conf.platforms

    labels: Dict[str, Optional[Union[str, List[str]]]] = {label.mosaic.JOB: None}

    # Filter instances
    if gpu_type is not None:
        labels[label.mosaic.compute_selectors.LABEL_GPU_TYPE] = gpu_type

    if gpu_num is not None:
        labels[label.mosaic.compute_selectors.LABEL_GPU_NUM] = gpu_num

    with console.status('Retrieving requested runs...'):
        contexts = [p.to_kube_context() for p in chosen_platforms]

        # Query for requested jobs
        all_pods, _ = list_pods_across_contexts(contexts=contexts, labels=labels)
        pod_grouping_by_job = group_pods_by_job(all_pods)

    display = MCLIRunDisplay(pod_grouping_by_job, status)
    display.print(output)

    return 0


def get_runs_argparser(subparsers):
    """Configures the ``mcli get runs`` argparser
    """
    # mcli get runs
    run_examples: str = """Examples:
    $ mcli get runs

    NAME                         PLATFORM   GPU_TYPE      GPU_NUM      CREATED_TIME     STATUS
    run-foo                      p-1        g0-type       8            05/06/22 1:58pm  succeeded
    run-bar                      p-2        g0-type       1            05/06/22 1:57pm  succeeded
    """
    runs_parser = subparsers.add_parser('runs',
                                        aliases=['run'],
                                        help='Get information on all of your existing runs across all platforms.',
                                        epilog=run_examples,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    runs_parser.add_argument('--platform', help='Filter to just runs on a specific platform')
    runs_parser.add_argument('--gpu-type', help='Filter to just runs on a specific GPU type')
    runs_parser.add_argument('--gpu-num', help='Filter to just runs of a specific number of GPUs')

    def _to_status(text: str) -> str:
        return to_camel_case(text).lower()

    status_options = [_to_status(state.value) for state in PodState]
    runs_parser.add_argument('--status',
                             choices=status_options,
                             type=_to_status,
                             help='Filter to just runs of a specific status')
    runs_parser.set_defaults(func=get_runs)

    return runs_parser
