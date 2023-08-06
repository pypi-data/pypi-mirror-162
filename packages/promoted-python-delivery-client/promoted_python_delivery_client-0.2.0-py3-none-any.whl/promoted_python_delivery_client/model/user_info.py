from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserInfo:
    user_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    log_user_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    is_internal_user: Optional[bool] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    ignore_usage: Optional[bool] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
