from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.IReason import IReason


#interface
class IDeleteMemberPayload(ABC):
    state:str
    reason:IReason
