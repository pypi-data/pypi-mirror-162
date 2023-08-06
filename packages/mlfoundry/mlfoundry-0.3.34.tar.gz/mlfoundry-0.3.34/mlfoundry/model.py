import logging
import os
import posixpath
import re
import tempfile
import typing
import uuid
from distutils.dir_util import copy_tree

import mlflow
from mlflow.entities import RunLog, RunStatus
from mlflow.tracking import MlflowClient

from mlfoundry.constants import RUN_LOGS_DIR
from mlfoundry.enums import ModelFramework
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.frameworks import get_model_registry
from mlfoundry.log_types import ModelArtifactRunLog

MODELS_LOG_DIR = posixpath.join(RUN_LOGS_DIR, "models")
MODEL_NAME_REGEX = re.compile(r"^[a-zA-Z0-9-_]*$")
logger = logging.getLogger(__name__)

# Right now we do not have concept of a model name.
# Now while saving the model as a run log, we need to give a key name.
# Right now I am hardcoding it to "model".
# This is not exposed to user at all.
# We should not change this default value at all.
DEFAULT_MODEL_NAME = "model"


def load_model_from_local_path(local_path: str):
    # this will fail if the model was not serialized
    # using tfy-mlflow-client
    # test all flavors from here

    model = mlflow.models.Model.load(local_path)
    for flavor in model.flavors.keys():
        try:
            framework = ModelFramework(flavor)
        except Exception:
            continue
        registry = get_model_registry(framework)
        return registry.load_model(local_path)
    raise MlFoundryException(f"unsupported frameworks {model.flavors.keys()}")


class ModelDriver:
    """ModelDriver."""

    def __init__(self, mlflow_client: MlflowClient, run_id: str):
        """__init__.

        :param mlflow_client:
        :type mlflow_client: MlflowClient
        :param run_id:
        :type run_id: str
        """
        self.mlflow_client: MlflowClient = mlflow_client
        self.run_id: str = run_id

    def _get_latest_run_log(
        self,
        model_name: str,
    ) -> typing.Optional[RunLog]:
        """
        Get latest run log under a run for a model (one with the largest step)
        If there are no run log then this function will return None.

        :param model_name: Name of the model. This will be just DEFAULT_MODEL_NAME
                           for now.
        :type model_name: str
        :rtype: typing.Optional[RunLog]
        """
        run_log = self.mlflow_client.get_latest_run_log(
            run_uuid=self.run_id,
            key=model_name,
            log_type=ModelArtifactRunLog.get_log_type(),
        )
        return run_log

    def _get_run_log(self, model_name: str, step: int) -> typing.Optional[RunLog]:
        """
        Get run log under a run for a model
        If there are no run log then this function will return None.

        :param model_name: Name of the model. This will be just DEFAULT_MODEL_NAME
                           for now.
        :type model_name: str
        :param step: step number (for which run_log is to be fetched)
        :rtype: typing.Optional[RunLog]
        """
        run_logs = self.mlflow_client.list_run_logs(
            run_uuid=self.run_id,
            key=model_name,
            log_type=ModelArtifactRunLog.get_log_type(),
            steps=[step],
        )

        if len(run_logs) == 0:
            return None
        return run_logs[0]

    def log_model(self, model, framework: str, step: int = 0, **kwargs):
        """
        Serialize and log a model for the current `run`. Each logged model is
            associated with a step. After logging model at a particular step
            we cannot overwrite it.

        Args:
            model: The model object
            framework (Union[enums.ModelFramework, str]): Model Framework. Ex:- pytorch,
                sklearn, tensorflow etc. The full list of supported frameworks can be
                found in `mlfoundry.enums.ModelFramework`.
            step (int, optional): step/iteration at which the model is being logged
                If not passed, `0` is set as the `step`.
            kwargs: Keyword arguments to be passed to the serializer.
        """
        model_name = DEFAULT_MODEL_NAME
        run_log = self._get_run_log(model_name, step)
        if run_log is not None:
            raise MlFoundryException(
                f"Model already logged with step: {step}, cannot overwrite."
            )
        framework = ModelFramework(framework)
        artifact_path = posixpath.join(
            MODELS_LOG_DIR, f"{model_name}-{step}-{uuid.uuid4().hex}"
        )
        # TODO (chiragjn): This is hack to temporarily use the mlflow.fluent API because
        #                  .log_model relies on run_id being stored in mlflow's global run stack
        created_run = None
        try:
            # Add to mlflow.fluent's global stack, hoping no other fluent run is running parallely
            created_run = mlflow.start_run(
                run_id=self.run_id,
                nested=True,  # necessary to avoid messing with existing run stack
            )
            get_model_registry(framework).log_model(
                model, artifact_path=artifact_path, **kwargs
            )
        finally:
            if created_run:
                # Remove from mlflow.fluent's global stack but keeping the run in Running mode
                mlflow.end_run(RunStatus.to_string(RunStatus.RUNNING))

        model_artifact_log = ModelArtifactRunLog(
            artifact_path=artifact_path, framework=framework
        )
        run_log = model_artifact_log.to_run_log(key=model_name, step=step)
        self.mlflow_client.insert_run_logs(run_uuid=self.run_id, run_logs=[run_log])
        logger.info("Model logged successfully")

    def get_model(
        self,
        dest_path: typing.Optional[str] = None,
        step: typing.Optional[int] = None,
        **kwargs,
    ):
        """
        Deserialize and return the logged model object for the current `run`
            and given step, returns the latest logged model(one logged at the
            largest step) if step is not passed

        Args:
            dest_path (Optional[str], optional): The path where the model is
            downloaded before deserializing.
            step (int, optional): step/iteration at which the model is being logged
                If not passed, the latest logged model (model logged with the
                highest step) is returned
            kwargs: Keyword arguments to be passed to the de-serializer.
        """
        model_name = DEFAULT_MODEL_NAME

        if step is None:
            run_log = self._get_latest_run_log(model_name)
        else:
            run_log = self._get_run_log(model_name, step)
        if run_log is None:
            raise MlFoundryException("Model is not logged")

        model_artifact_log = ModelArtifactRunLog.from_run_log(run_log)
        model_uri = self.mlflow_client.download_artifacts(
            self.run_id, path=model_artifact_log.artifact_path, dst_path=dest_path
        )
        model_framework = get_model_registry(model_artifact_log.framework)
        return model_framework.load_model(
            model_uri,
            **kwargs,
        )

    def download_model(self, dest_path: str, step: typing.Optional[int]):
        """
        Download logged model for the current `run` at a particular `step` in a
            local directory. Downloads the latest logged run (one logged at the
            largest step) if step is not passed.xs


        Args:
            dest_path (str): local directory where the model will be downloaded.
                if `dest_path` does not exist, it will be created.
                If dest_path already exist, it should be an empty directory.
            step (int, optional): step/iteration at which the model is being logged
                If not passed, the latest logged model (model logged with the
                highest step) is downloaded
        """
        model_name = DEFAULT_MODEL_NAME
        if step is None:
            run_log = self._get_latest_run_log(model_name)
        else:
            run_log = self._get_run_log(model_name, step)

        if run_log is None:
            raise MlFoundryException("Model is not logged")

        model_artifact_log = ModelArtifactRunLog.from_run_log(run_log)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        elif any(os.scandir(dest_path)):
            raise MlFoundryException("model download path should be empty")
        with tempfile.TemporaryDirectory() as local_dir:
            self.mlflow_client.download_artifacts(
                self.run_id, path=model_artifact_log.artifact_path, dst_path=local_dir
            )
            model_dir = os.path.join(
                local_dir, os.path.normpath(model_artifact_log.artifact_path)
            )
            copy_tree(model_dir, dest_path)
