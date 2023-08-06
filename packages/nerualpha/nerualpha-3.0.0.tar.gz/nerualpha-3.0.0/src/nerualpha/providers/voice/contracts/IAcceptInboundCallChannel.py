from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.IAcceptInboundCallEndpoint import IAcceptInboundCallEndpoint
from nerualpha.providers.voice.contracts.ILeg import ILeg


#interface
class IAcceptInboundCallChannel(ABC):
    type_:str
    leg_id:str
    from_:IAcceptInboundCallEndpoint
    to:IAcceptInboundCallEndpoint
    leg_ids:List[ILeg]
