from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.ICallTimestamp import ICallTimestamp
from nerualpha.providers.voice.contracts.IAcceptInboundCallChannel import IAcceptInboundCallChannel


#interface
class IAcceptInboundCallResponse(ABC):
    id:str
    user_id:str
    state:str
    timestamp:ICallTimestamp
    channel:IAcceptInboundCallChannel
    href:str
