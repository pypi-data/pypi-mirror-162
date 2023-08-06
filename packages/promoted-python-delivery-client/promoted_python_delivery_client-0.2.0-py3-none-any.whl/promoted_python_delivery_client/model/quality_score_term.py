from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from promoted_python_delivery_client.model.term_conditional_evaluation import TermConditionalEvaluation


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class QualityScoreTerm:
    fetch_high: float
    fetch_low: float
    offset: float
    weight: float
    term_conditional_evaluation: TermConditionalEvaluation
