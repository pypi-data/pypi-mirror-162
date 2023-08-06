from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import Dict


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Properties:
    struct: Dict[str, object]

