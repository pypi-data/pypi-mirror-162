from dataclasses import dataclass
from typing import Optional
from promoted_python_delivery_client.model.execution_server import ExecutionServer
from promoted_python_delivery_client.model.response import Response


@dataclass
class DeliveryResponse:
    response: Response
    client_request_id: Optional[str]
    execution_server: ExecutionServer
