import concurrent.futures
import copy
import logging
from typing import List, Optional
import time
import uuid
from promoted_python_delivery_client.client.api_delivery import APIDelivery
from promoted_python_delivery_client.client.api_metrics import APIMetrics
from promoted_python_delivery_client.client.delivery_request import DeliveryRequest
from promoted_python_delivery_client.client.delivery_response import DeliveryResponse
from promoted_python_delivery_client.client.sampler import Sampler
from promoted_python_delivery_client.client.sdk_delivery import SDKDelivery
from promoted_python_delivery_client.model.client_info import ClientInfo
from promoted_python_delivery_client.model.client_type import ClientType
from promoted_python_delivery_client.model.cohort_arm import CohortArm
from promoted_python_delivery_client.model.cohort_membership import CohortMembership
from promoted_python_delivery_client.model.delivery_execution import DeliveryExecution
from promoted_python_delivery_client.model.delivery_log import DeliveryLog
from promoted_python_delivery_client.model.execution_server import ExecutionServer
from promoted_python_delivery_client.model.log_request import LogRequest
from promoted_python_delivery_client.model.request import Request
from promoted_python_delivery_client.model.response import Response
from promoted_python_delivery_client.model.timing import Timing
from promoted_python_delivery_client.model.traffic_type import TrafficType


SERVER_VERSION = "python.1.0.0"

# Executor to run metrics logging in the background.
DEFAULT_METRICS_THREAD_POOL_SIZE = 5

# Default number of maximum request insertion passed to Delivery API.
DEFAULT_MAX_REQUEST_INSERTIONS = 1000


class PromotedDeliveryClient:
    def __init__(self,
                 delivery_endpoint: str,
                 delivery_api_key: str,
                 metrics_endpoint: str,
                 metrics_api_key: str,
                 delivery_timeout_millis: Optional[int] = None,
                 metrics_timeout_millis: Optional[int] = None,
                 max_request_insertions: Optional[int] = DEFAULT_MAX_REQUEST_INSERTIONS,
                 shadow_traffic_delivery_rate: Optional[float] = 0,
                 perform_checks: Optional[bool] = False) -> None:
        self.metrics_endpoint = metrics_endpoint
        self.metrics_api_key = metrics_api_key
        self.metrics_timeout_millis = metrics_timeout_millis
        self.max_request_insertions = max_request_insertions
        self.sampler = Sampler()
        self.sdk_delivery = SDKDelivery()
        self.api_delivery = APIDelivery(delivery_endpoint, delivery_api_key, delivery_timeout_millis)
        self.api_metrics = APIMetrics(metrics_endpoint, metrics_api_key, metrics_timeout_millis)

        if shadow_traffic_delivery_rate is not None and (shadow_traffic_delivery_rate < 0 or shadow_traffic_delivery_rate > 1):
            raise ValueError("shadow traffic delivery rate must be between 0 and 1")
        self.shadow_traffic_delivery_rate = shadow_traffic_delivery_rate

        self.perform_checks = perform_checks if perform_checks is not None else False

        self.executor = concurrent.futures.ThreadPoolExecutor(DEFAULT_METRICS_THREAD_POOL_SIZE)

    def deliver(self, request: DeliveryRequest) -> DeliveryResponse:
        should_send_shadow_traffic = self._should_send_shadow_traffic()
        exec_svr = ExecutionServer.SDK
        cohort_membership = self._check_cohort_membership(request)
        attempted_delivery_api = False
        self._fill_request_fields(request.request)

        if request.only_log or not self._should_apply_treatment(cohort_membership):
            resp = self.sdk_delivery.run_delivery(request)
        else:
            attempted_delivery_api = True
            try:
                resp = self.api_delivery.run_delivery(request)
                exec_svr = ExecutionServer.API
            except Exception as ex:
                logging.error("Error calling delivery", exc_info=ex)
                resp = self.sdk_delivery.run_delivery(request)

        # If delivery happened client-side, log the insertions to metrics API.
        if exec_svr != ExecutionServer.API or cohort_membership is not None:
            self.executor.submit(self._log_to_metrics, request, resp, cohort_membership, exec_svr)

        # Check to see if we should do shadow traffic.
        if (not attempted_delivery_api) and should_send_shadow_traffic:
            self.executor.submit(self._deliver_shadow_traffic, request)

        return DeliveryResponse(resp, request.request.client_request_id, exec_svr)

    def _log_to_metrics(self,
                        delivery_request: DeliveryRequest,
                        response: Response,
                        cohort_membership: Optional[CohortMembership],
                        exec_svr: ExecutionServer) -> None:
        log_request = self._create_log_request(delivery_request, response, cohort_membership, exec_svr)
        try:
            self.api_metrics.run_metrics_logging(log_request)
        except Exception as ex:
            logging.error("Error logging to metrics", exc_info=ex)


    def _create_log_request(self,
                        delivery_request: DeliveryRequest,
                        response: Response,
                        cohort_membership: Optional[CohortMembership],
                        exec_svr: ExecutionServer) -> LogRequest:
        request = delivery_request.request

        delivery_logs: List[DeliveryLog] = []
        cohort_memberships: List[CohortMembership] = []

        if exec_svr != ExecutionServer.API:
            delivery_logs.append(DeliveryLog(
              request=request,
              response=response,
              execution=DeliveryExecution(execution_server=exec_svr, server_version=SERVER_VERSION))
            )

        if cohort_membership is not None:
            cohort_memberships.append(cohort_membership)

        log_request = LogRequest(
          user_info=request.user_info,
          client_info=request.client_info,
          platform_id=request.platform_id,
          timing=request.timing,
          cohort_membership=cohort_memberships,
          delivery_log=delivery_logs)

        return log_request

    def _deliver_shadow_traffic(self, delivery_request: DeliveryRequest) -> None:
        # We need a clone of the request so that we can safely modify the ClientInfo for shadow traffic.
        request_to_send = copy.deepcopy(delivery_request)

        # We ensured earlier that ClientInfo was filled in.
        assert request_to_send.request.client_info is not None

        request_to_send.request.client_info.client_type = ClientType.SERVER
        request_to_send.request.client_info.traffic_type = TrafficType.SHADOW

        try:
            self.api_delivery.run_delivery(request_to_send)
        except Exception as ex:
            logging.error("Error sending shadow traffic", exc_info=ex)

    def _should_apply_treatment(self, cohort_membership: Optional[CohortMembership] = None) -> bool:
        if cohort_membership is None:
            return True
        return cohort_membership.arm is None or cohort_membership.arm != CohortArm.CONTROL

    def _check_cohort_membership(self, request: DeliveryRequest) -> Optional[CohortMembership]:
        if request.experiment is None:
            return None
        cohort_membership = CohortMembership(
            request.experiment.cohort_id,
            request.experiment.arm,
            request.experiment.platform_id,
            request.experiment.user_info,
            request.experiment.timing)

        # Fall back to request values for things not set on the experiment.
        if cohort_membership.platform_id is None:
            cohort_membership.platform_id = request.request.platform_id
        if cohort_membership.user_info is None:
            cohort_membership.user_info = request.request.user_info
        if cohort_membership.timing is None:
            cohort_membership.timing = request.request.timing

        return cohort_membership

    def _should_send_shadow_traffic(self) -> bool:
        return self.shadow_traffic_delivery_rate is not None and self.shadow_traffic_delivery_rate> 0 and self.sampler.sample_random(self.shadow_traffic_delivery_rate)

    def _fill_request_fields(self, request: Request) -> None:
        if request.client_info is None:
            request.client_info = ClientInfo()
        request.client_info.client_type = ClientType.SERVER
        request.client_info.traffic_type = TrafficType.PRODUCTION

        self._ensure_client_request_id(request)

        self._ensure_client_timestamp(request)

    def _ensure_client_request_id(self, request: Request) -> None:
        if request.client_request_id is None or not request.client_request_id.strip():
            request.client_request_id = str(uuid.uuid4())

    def _ensure_client_timestamp(self, request: Request) -> None:
        if request.timing is None:
            request.timing = Timing()
        if request.timing.client_log_timestamp is None:
            request.timing.client_log_timestamp = current_time_millis()


def current_time_millis():
    return round(time.time() * 1000)
