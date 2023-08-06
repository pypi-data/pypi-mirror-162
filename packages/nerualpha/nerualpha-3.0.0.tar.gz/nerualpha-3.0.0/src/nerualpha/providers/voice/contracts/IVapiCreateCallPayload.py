from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.IPhoneContact import IPhoneContact


#interface
class IVapiCreateCallPayload(ABC):
    from_:IPhoneContact
    to:List[IPhoneContact]
    ncco:List[Dict[str,object]]
