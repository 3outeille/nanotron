from abc import ABC, abstractmethod
from typing import List

from nanotron.logging import LogItem


class BaseLogger(ABC):
    @abstractmethod
    def add_scalars_from_list(self, log_entries: List[LogItem], iteration_step: int):
        ...
