import logging
import requests
from promoted_python_delivery_client.client.delivery_request import DeliveryRequest
from promoted_python_delivery_client.client.delivery_request_state import DeliveryRequestState
from promoted_python_delivery_client.model.response import Response


class APIDelivery:
    def __init__(self,
                 endpoint: str,
                 api_key: str,
                 timeout: int,
                 max_request_insertions: int,
                 warmup: bool = False) -> None:
        self.endpoint = endpoint
        self.max_request_insertions = max_request_insertions
        self.headers = {"x-api-key": api_key}
        self.timeout_in_seconds = timeout / 1000
        if warmup:
            self._run_warmup()

    def run_delivery(self, delivery_request: DeliveryRequest) -> Response:
        state = DeliveryRequestState(delivery_request)

        request = state.get_request_to_send(self.max_request_insertions)
        payload = request.to_json()  # type: ignore this is from dataclass_json
        r = requests.post(url=self.endpoint,
                          data=payload,
                          timeout=self.timeout_in_seconds,
                          headers=self.headers)
        if r.status_code != 200:
            logging.error(f"Error calling delivery API {r.status_code}")
            raise requests.HTTPError("error calling delivery API")
        return state.get_response_to_return(Response.from_json(r.content))  # type: ignore this is from dataclass_json

    def _run_warmup(self):
        warmup_endpoint = self.endpoint.replace("/deliver", "/healthz")
        for i in range(0, 20):
            r = requests.get(url=warmup_endpoint, headers=self.headers)
            if r.status_code != 200:
                logging.warning(f"Error during warmup {r.status_code}")
