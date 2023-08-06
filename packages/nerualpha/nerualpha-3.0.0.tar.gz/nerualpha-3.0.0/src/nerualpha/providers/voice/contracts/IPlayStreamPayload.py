from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.IPlayStreamBody import IPlayStreamBody


#interface
class IPlayStreamPayload(ABC):
    type_:str
    to:str
    body:IPlayStreamBody
