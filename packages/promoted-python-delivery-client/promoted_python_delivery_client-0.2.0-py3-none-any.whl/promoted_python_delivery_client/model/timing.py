from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Timing:
    client_log_timestamp: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    event_api_timestamp: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    log_timestamp: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
