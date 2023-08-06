from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List
from promoted_python_delivery_client.model.quality_score_term import QualityScoreTerm


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class QualityScoreConfig:
    weighted_sum_term: List[QualityScoreTerm]
