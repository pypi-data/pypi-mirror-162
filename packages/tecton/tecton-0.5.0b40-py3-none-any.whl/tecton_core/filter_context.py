from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FilterContext:
    start_time: Optional[datetime]
    end_time: Optional[datetime]
