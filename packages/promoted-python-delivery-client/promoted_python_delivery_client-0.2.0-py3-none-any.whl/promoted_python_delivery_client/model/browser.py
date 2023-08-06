from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from promoted_python_delivery_client.model.client_hints import ClientHints
from promoted_python_delivery_client.model.size import Size


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Browser:
    client_hints: ClientHints
    user_agent: str
    viewport_size: Size
