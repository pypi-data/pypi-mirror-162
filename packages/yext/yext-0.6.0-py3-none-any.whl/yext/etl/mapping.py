from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Mapping:
    source_field: str
    kg_field: str
    transform: Optional[Callable] = lambda x: x
    required: Optional[bool] = True