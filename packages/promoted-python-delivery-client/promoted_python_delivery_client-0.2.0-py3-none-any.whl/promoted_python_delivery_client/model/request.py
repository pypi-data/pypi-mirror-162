from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import List, Optional
from promoted_python_delivery_client.model.blender_config import BlenderConfig
from promoted_python_delivery_client.model.client_info import ClientInfo
from promoted_python_delivery_client.model.insertion import Insertion
from promoted_python_delivery_client.model.paging import Paging
from promoted_python_delivery_client.model.properties import Properties
from promoted_python_delivery_client.model.timing import Timing
from promoted_python_delivery_client.model.use_case import UseCase
from promoted_python_delivery_client.model.user_info import UserInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Request:
    insertion: List[Insertion]
    user_info: Optional[UserInfo] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    client_request_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    request_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    client_info: Optional[ClientInfo] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    search_query: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    use_case: Optional[UseCase] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    auto_view_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    blender_config: Optional[BlenderConfig] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    debug: Optional[bool] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    paging: Optional[Paging] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    platform_id: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    properties: Optional[Properties] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    session_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    timing: Optional[Timing] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    view_id: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
