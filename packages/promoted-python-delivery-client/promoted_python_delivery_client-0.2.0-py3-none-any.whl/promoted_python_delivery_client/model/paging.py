from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Paging:
    size: int
    offset: Optional[int] = 0
    paging_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    cursor: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
