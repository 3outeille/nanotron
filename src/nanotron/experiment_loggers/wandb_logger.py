from typing import List

import wandb
from huggingface_hub.utils import disable_progress_bars

from nanotron.experiment_loggers import LogItem
from nanotron.experiment_loggers.interface import BaseLogger
from nanotron.logging import get_logger

disable_progress_bars()

logger = get_logger(__name__)


class WandBLogger(BaseLogger):
    def add_scalars_from_list(self, log_entries: List[LogItem], iteration_step: int):
        wandb.log({log_item.tag: log_item.scalar_value for log_item in log_entries}, step=iteration_step)
