from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.session.requestInterface import RequestInterface
from nerualpha.session.requestInterfaceForCallbacks import RequestInterfaceForCallbacks
from nerualpha.providers.scheduler.contracts.schedulePayload import SchedulePayload
from nerualpha.providers.scheduler.contracts.IStartAtParams import IStartAtParams


#interface
class IScheduler(ABC):
    @abstractmethod
    def startAt(self,params):
        pass
    @abstractmethod
    def cancel(self,scheduleId):
        pass
