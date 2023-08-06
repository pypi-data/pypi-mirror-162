from dataclasses import dataclass
from typing import Optional
from promoted_python_delivery_client.client.insertion_page_type import InsertionPageType
from promoted_python_delivery_client.model.cohort_membership import CohortMembership
from promoted_python_delivery_client.model.request import Request


@dataclass
class DeliveryRequest:
    request: Request
    experiment: Optional[CohortMembership] = None
    only_log: bool = False
    insertion_page_type: InsertionPageType = InsertionPageType.UNPAGED
