from dataclasses import dataclass, field
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod


class NumberFeature:
    SMS = "SMS"
    Voice = "VOICE"
    MMS = "MMS"
