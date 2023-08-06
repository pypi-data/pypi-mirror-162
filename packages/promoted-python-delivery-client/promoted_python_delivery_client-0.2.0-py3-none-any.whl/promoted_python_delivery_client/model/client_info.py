from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional
from promoted_python_delivery_client.model.client_type import ClientType

from promoted_python_delivery_client.model.traffic_type import TrafficType


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClientInfo:
    client_type: Optional[ClientType] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    traffic_type: Optional[TrafficType] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
