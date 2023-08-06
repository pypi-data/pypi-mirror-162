from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from promoted_python_delivery_client.model.delivery_execution import DeliveryExecution
from promoted_python_delivery_client.model.response import Response
from promoted_python_delivery_client.model.request import Request


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeliveryLog:
    request: Request
    response: Response
    execution: DeliveryExecution
