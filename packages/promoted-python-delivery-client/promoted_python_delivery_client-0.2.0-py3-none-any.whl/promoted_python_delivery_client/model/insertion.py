from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional
from promoted_python_delivery_client.model.client_info import ClientInfo
from promoted_python_delivery_client.model.properties import Properties
from promoted_python_delivery_client.model.timing import Timing
from promoted_python_delivery_client.model.user_info import UserInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Insertion:
    content_id: str
    position: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    insertion_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    retrieval_rank: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    retrieval_score: Optional[float] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    view_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    user_info: Optional[UserInfo] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    client_info: Optional[ClientInfo] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    auto_view_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    platform_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    properties: Optional[Properties] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    session_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    timing: Optional[Timing] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
