from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.session.requestInterface import RequestInterface
from nerualpha.providers.scheduler.schedulerActions import SchedulerActions
from nerualpha.session.actionPayload import ActionPayload
from nerualpha.providers.scheduler.IScheduler import IScheduler
from nerualpha.providers.scheduler.contracts.startAtPayload import StartAtPayload
from nerualpha.providers.scheduler.contracts.schedulePayload import SchedulePayload
from nerualpha.providers.scheduler.contracts.IStartAtParams import IStartAtParams
from nerualpha.session.ISession import ISession
from nerualpha.session.requestInterfaceForCallbacks import RequestInterfaceForCallbacks
from nerualpha.session.IPayloadWithCallback import IPayloadWithCallback

@dataclass
class Scheduler(IScheduler):
    session: ISession
    provider: str = field(default = "vonage-scheduler")
    def __init__(self,session):
        self.session = session
    
    def startAt(self,params):
        startAtPayload = StartAtPayload()
        startAtPayload.startAt = params.startAt
        startAtPayload.callback = self.session.wrapCallback(params.callback,[])
        if params.payload is not None:
            startAtPayload.payload = params.payload
        
        if params.interval is not None:
            startAtPayload.interval = params.interval
        
        if params.id is not None:
            startAtPayload.id = params.id
        
        action = ActionPayload(self.provider,SchedulerActions.Create,startAtPayload)
        return RequestInterfaceForCallbacks(self.session,action)
    
    def listAll(self):
        action = ActionPayload(self.provider,SchedulerActions.List,None)
        return RequestInterface(self.session,action)
    
    def get(self,scheduleId):
        payload = SchedulePayload(scheduleId)
        action = ActionPayload(self.provider,SchedulerActions.Get,payload)
        return RequestInterface(self.session,action)
    
    def cancel(self,scheduleId):
        payload = SchedulePayload(scheduleId)
        action = ActionPayload(self.provider,SchedulerActions.Cancel,payload)
        return RequestInterface(self.session,action)
    
    def reprJSON(self):
        dict = {}
        keywordsMap = {"from_":"from","del_":"del","import_":"import","type_":"type"}
        for key in self.__dict__:
            val = self.__dict__[key]

            if type(val) is list:
                parsedList = []
                for i in val:
                    if hasattr(i,'reprJSON'):
                        parsedList.append(i.reprJSON())
                    else:
                        parsedList.append(i)
                val = parsedList

            if hasattr(val,'reprJSON'):
                val = val.reprJSON()
            if key in keywordsMap:
                key = keywordsMap[key]
            dict.__setitem__(key.replace('_hyphen_', '-'), val)
        return dict
