from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.session.IPayloadWithCallback import IPayloadWithCallback
from nerualpha.providers.vonageAI.contracts.IImportPayload import IImportPayload


#interface
class IVonageAiImportModelPayload(IPayloadWithCallback):
    import_:IImportPayload
