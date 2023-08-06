from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List
from promoted_python_delivery_client.model.client_hint_brand import ClientHintBrand


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClientHints:
    architecture: str
    brand: List[ClientHintBrand]
    is_mobile: bool
    platform: str
    platform_version: str
    ua_full_version: str
