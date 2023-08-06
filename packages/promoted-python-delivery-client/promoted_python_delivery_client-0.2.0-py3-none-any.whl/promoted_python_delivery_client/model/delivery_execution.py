from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from promoted_python_delivery_client.model.execution_server import ExecutionServer


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeliveryExecution:
    execution_server: ExecutionServer
    server_version: str
