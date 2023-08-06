from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.ICreateEventResponse import ICreateEventResponse


#interface
class IMuteOnResponse(ICreateEventResponse):
    pass
