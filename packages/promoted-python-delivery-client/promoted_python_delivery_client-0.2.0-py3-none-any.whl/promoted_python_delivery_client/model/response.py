from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List, Optional

from promoted_python_delivery_client.model.insertion import Insertion
from promoted_python_delivery_client.model.paging_info import PagingInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Response:
    insertion: List[Insertion]
    paging_info: Optional[PagingInfo] = None
