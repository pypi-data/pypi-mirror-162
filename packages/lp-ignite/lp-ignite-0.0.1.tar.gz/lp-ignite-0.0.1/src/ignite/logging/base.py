import numbers
import warnings
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from typing import Any

class BaseHandler(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, logger, event_name):
        pass
