from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List
from promoted_python_delivery_client.model.blender_rule import BlenderRule
from promoted_python_delivery_client.model.quality_score_config import QualityScoreConfig


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BlenderConfig:
    blender_rule: List[BlenderRule]
    quality_score_config: QualityScoreConfig
