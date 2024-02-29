from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from nanotron.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HubTensorBoardLoggerConfig:
    """Arguments related to the HF Tensorboard logger"""

    tensorboard_dir: Path
    repo_id: str
    push_to_hub_interval: int
    repo_public: bool = False

    def __post_init__(self):
        if isinstance(self.tensorboard_dir, str):
            self.tensorboard_dir = Path(self.tensorboard_dir)


@dataclass
class TensorboardLoggerConfig:
    """Arguments related to the local Tensorboard logger"""

    tensorboard_dir: Path
    flush_secs: int = 30

    def __post_init__(self):
        if isinstance(self.tensorboard_dir, str):
            self.tensorboard_dir = Path(self.tensorboard_dir)


@dataclass
class WandbLoggerConfig:
    """Arguments related to the local Wandb logger"""

    wandb_project: str = ""
    wandb_entity: Optional[str] = None

    def __post_init__(self):
        assert self.wandb_project != "", "Please specify a wandb_project"


@dataclass
class NanotronExperimentLoggerArgs:
    """Arguments related to logging"""

    tensorboard_logger: Optional[Union[HubTensorBoardLoggerConfig, TensorboardLoggerConfig]] = None
    wandb_logger: Optional[WandbLoggerConfig] = None

    def __post_init__(self):
        if self.wandb_logger is not None:
            assert self.tensorboard_logger is not None, "Wandb logger requires a tensorboard logger"
