from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.messages.contracts.IBaseMessage import IBaseMessage
from nerualpha.providers.messages.contracts.IImagePayload import IImagePayload


#interface
class IWhatsappImageMessage(IBaseMessage):
    image:IImagePayload
