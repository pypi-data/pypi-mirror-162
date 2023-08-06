from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Location:
    accuracy_in_meters: float
    latitude: float
    longitude: float
