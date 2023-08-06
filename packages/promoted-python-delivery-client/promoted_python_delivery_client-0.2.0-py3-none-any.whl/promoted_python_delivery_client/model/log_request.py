from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import List, Optional
from promoted_python_delivery_client.model.client_info import ClientInfo
from promoted_python_delivery_client.model.delivery_log import DeliveryLog
from promoted_python_delivery_client.model.cohort_membership import CohortMembership
from promoted_python_delivery_client.model.timing import Timing
from promoted_python_delivery_client.model.user_info import UserInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LogRequest:
    delivery_log: List[DeliveryLog]
    cohort_membership: Optional[List[CohortMembership]] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    user_info: Optional[UserInfo] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    client_info: Optional[ClientInfo] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    platform_id: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    timing: Optional[Timing] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
