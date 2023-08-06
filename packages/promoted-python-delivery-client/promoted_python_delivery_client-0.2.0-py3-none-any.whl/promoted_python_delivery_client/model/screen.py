from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from promoted_python_delivery_client.model.size import Size


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Screen:
    scale: float
    size: Size
