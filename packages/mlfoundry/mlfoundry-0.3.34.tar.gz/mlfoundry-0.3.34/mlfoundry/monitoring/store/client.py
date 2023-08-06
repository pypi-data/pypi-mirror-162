import atexit
import json
import logging
import os
import queue
import threading
import typing
import uuid
from datetime import datetime

from mlfoundry.exceptions import MlFoundryException
from mlfoundry.monitoring.entities import (
    Actual,
    ActualPacket,
    BasePacket,
    Prediction,
    PredictionPacket,
)
from mlfoundry.monitoring.store.constants import (
    FLUSH_BATCH_SIZE_ENV_VAR,
    FLUSH_INTERVAL_ENV_VAR,
    MAX_QUEUE_SIZE_ENV_VAR,
)
from mlfoundry.monitoring.store.repositories import get_monitoring_store
from mlfoundry.monitoring.store.worker import MonitoringStoreWorker

logger = logging.getLogger(__name__)


def _check_shutdown(func):
    def wrapper(self, *args, **kwargs):
        if self._is_shutdown:
            raise MlFoundryException("cannot execute after client is shutdown")
        return func(self, *args, **kwargs)

    return wrapper


class MonitoringClient:
    def __init__(self, monitoring_uri: str, model_id: str, model_version: str):
        self._is_shutdown = False

        self.monitoring_store = get_monitoring_store(host_uri=monitoring_uri)
        self.model_id = model_id
        self.model_version = model_version
        self.dataset_id = self.monitoring_store.get_dataset_id_from_model_id(model_id)

        max_queue_size = int(os.getenv(MAX_QUEUE_SIZE_ENV_VAR, "10000"))
        flush_interval = float(os.getenv(FLUSH_INTERVAL_ENV_VAR, "5"))
        flush_batch_size = int(os.getenv(FLUSH_BATCH_SIZE_ENV_VAR, "300"))

        if max_queue_size <= 0:
            raise MlFoundryException(
                f"{MAX_QUEUE_SIZE_ENV_VAR} should be a positive number"
            )

        self.task_queue: "queue.Queue[BasePacket]" = queue.Queue(max_queue_size)
        self.worker_terminate_event = threading.Event()

        if flush_interval <= 0:
            raise MlFoundryException(
                f"{FLUSH_INTERVAL_ENV_VAR} should be a positive number"
            )
        if flush_batch_size <= 0 or flush_batch_size > max_queue_size:
            raise MlFoundryException(
                f"{FLUSH_BATCH_SIZE_ENV_VAR} should be positive"
                f" and lower than {MAX_QUEUE_SIZE_ENV_VAR}"
            )

        self.worker: MonitoringStoreWorker = MonitoringStoreWorker(
            task_queue=self.task_queue,
            terminate_event=self.worker_terminate_event,
            monitoring_store=self.monitoring_store,
            flush_interval=flush_interval,
            flush_every_num_message=flush_batch_size,
        )
        atexit.register(self._shutdown)
        self.worker.start()

    @staticmethod
    def generate_id_from_data(
        features: typing.Dict, timestamp: typing.Optional[datetime] = None
    ):
        data_str = json.dumps(features, sort_keys=True)
        if timestamp:
            data_str += timestamp.isoformat()
        return uuid.uuid5(uuid.NAMESPACE_X500, data_str).hex

    @staticmethod
    def generate_random_id():
        return uuid.uuid4().hex

    def _generate_prediction_packet_from_data(
        self, prediction: Prediction
    ) -> PredictionPacket:

        return PredictionPacket(
            model_id=self.model_id,
            model_version=self.model_version,
            dataset_id=self.dataset_id,
            prediction=prediction,
        )

    def _generate_actual_packet_from_data(self, actual: Actual):
        return ActualPacket(
            model_id=self.model_id,
            model_version=self.model_version,
            dataset_id=self.dataset_id,
            actual=actual,
        )

    def _put_in_queue(self, inference_packet: BasePacket):
        try:
            self.task_queue.put_nowait(inference_packet)
        except queue.Full as ex:
            raise MlFoundryException(
                "task queue is full\n"
                f"current task queue length is {self.task_queue.maxsize}\n"
                "consider increasing the task queue length using "
                f"{MAX_QUEUE_SIZE_ENV_VAR} environment variable"
            ) from ex

    @_check_shutdown
    def log_prediction(self, prediction: Prediction):
        prediction_packet = self._generate_prediction_packet_from_data(prediction)
        self._put_in_queue(prediction_packet)

    @_check_shutdown
    def log_actual(self, actual: Actual):
        actual_packet = self._generate_actual_packet_from_data(actual)
        self._put_in_queue(actual_packet)

    @_check_shutdown
    def log_predictions(self, predictions: typing.List[Prediction]):
        for prediction in predictions:
            self.log_prediction(prediction)

    @_check_shutdown
    def log_actuals(self, actuals: typing.List[Actual]):
        for actual in actuals:
            self.log_actual(actual)

    def _flush(self):
        logger.debug(
            f"flushing task queue, {self.task_queue.qsize()} items in the queue"
        )
        self.task_queue.join()
        logger.debug("task queue flushed")

    def _shutdown(self):
        if self._is_shutdown:
            return
        logger.debug("shutting down worker and client")
        self._is_shutdown = True
        # NOTE: We initialize the monitoring store at first in the constructor
        # The task_queue, worker is defined later.
        # There is a chance that monitoring  store initialization will throw error,
        # in that case, shutdown will be called (__del__) but self.task_queue would not have
        # been initialized yet.
        if hasattr(self, "task_queue"):
            self._flush()
        if hasattr(self, "worker_terminate_event"):
            logger.debug("setting worker termination event")
            self.worker_terminate_event.set()
        if hasattr(self, "worker"):
            logger.debug("waiting for worker to terminate")
            self.worker.join()

    def __del__(self):
        self._shutdown()
