from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.session.IActionPayload import IActionPayload
from nerualpha.session.ICommandHeaders import ICommandHeaders

T = TypeVar("T")


#interface
class ICommand(ABC,Generic[T]):
    header:ICommandHeaders
    actions:List[IActionPayload[T]]
