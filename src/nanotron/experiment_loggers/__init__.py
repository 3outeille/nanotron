# flake8: noqa
from nanotron.logging import LoggerWriter, LogItem
from nanotron.utils import _can_import_from_module, _is_package_available

from .utils import flatten_dict, obj_to_markdown

__all__ = ["LogItem", "LoggerWriter"]

tensorboardx_available = _is_package_available("tensorboardX")

if tensorboardx_available:
    from tensorboardX import SummaryWriter

    from .hub_tensorboard_logger import BatchSummaryWriter

    __all__ = __all__ + ["BatchSummaryWriter", "SummaryWriter"]
else:
    print("TensorboardX is not available. Please install tensorboardX")

huggingface_hub_available = _is_package_available("huggingface_hub")
hf_tensorboard_logger_available = _can_import_from_module("huggingface_hub", "HFSummaryWriter")

if huggingface_hub_available and hf_tensorboard_logger_available:
    from nanotron.experiment_loggers.hub_tensorboard_logger import HubSummaryWriter

    __all__ = __all__ + ["HubSummaryWriter"]
else:
    print("Huggingface Hub is not available. Please install huggingface_hub")

wandb_available = _is_package_available("wandb")

if wandb_available:
    from .wandb_logger import WandBLogger

    __all__ = __all__ + ["WandBLogger"]
else:
    print("WandB is not available. Please install wandb")
