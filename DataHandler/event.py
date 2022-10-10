from dataclasses import dataclass, field
from pandas import Timestamp

from typing import List

@dataclass
class BarEvent:
    type_: str  = field(init=False, default="BAR")
    symbols: dict = field(init=False, default_factory=dict)
    date: Timestamp

@dataclass
class SentimentEvent:
    type_: str  = field(init=False, default="SENTIMENT")
    symbols: List[str] = field(init=False, default_factory=dict)
    date: Timestamp
