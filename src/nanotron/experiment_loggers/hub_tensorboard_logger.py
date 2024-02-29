from typing import List

from huggingface_hub import HFSummaryWriter
from huggingface_hub.utils import disable_progress_bars
from tensorboardX import SummaryWriter

from nanotron.experiment_loggers import LogItem
from nanotron.experiment_loggers.interface import BaseLogger
from nanotron.logging import get_logger

disable_progress_bars()

logger = get_logger(__name__)


class HubSummaryWriter(BaseLogger, HFSummaryWriter):
    def add_scalars_from_list(self, log_entries: List[LogItem], iteration_step: int):
        for log_item in log_entries:
            super().add_scalar(log_item.tag, log_item.scalar_value, iteration_step)


class BatchSummaryWriter(BaseLogger, SummaryWriter):
    def add_scalars_from_list(self, log_entries: List[LogItem], iteration_step: int):
        for log_item in log_entries:
            super().add_scalar(log_item.tag, log_item.scalar_value, iteration_step)
