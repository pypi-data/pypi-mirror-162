from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from promoted_python_delivery_client.model.cohort_arm import CohortArm


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CohortMembership:
    cohort_id: str
    arm: CohortArm
