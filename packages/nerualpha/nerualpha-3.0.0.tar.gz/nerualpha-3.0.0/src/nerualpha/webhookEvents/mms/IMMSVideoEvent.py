from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.webhookEvents.IUrlObject import IUrlObject
from nerualpha.webhookEvents.mms.IMMSEvent import IMMSEvent


#interface
class IMMSVideoEvent(IMMSEvent):
    video:IUrlObject
