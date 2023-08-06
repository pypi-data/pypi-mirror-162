from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from json import JSONDecoder


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Size(JSONDecoder):
    height: int
    width: int
