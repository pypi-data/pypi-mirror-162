from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermConditionalEvaluation:
    attribute_name: str
    hashed_attribute: int
    value_if_false: float
    eval_method: object
