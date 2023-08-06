from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.numbers.contracts.IBaseNumberOptions import IBaseNumberOptions


#interface
class ISearchNumbersOptions(IBaseNumberOptions):
    country:str
    type_:str
    pattern:str
    search_pattern:str
    features:List[str]
    size:str
    index:str
