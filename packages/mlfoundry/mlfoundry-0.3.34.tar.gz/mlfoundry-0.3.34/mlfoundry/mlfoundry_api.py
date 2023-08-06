"""
# TO independently test this module, you can run the example in the path
python examples/sklearn/iris_train.py

Besides running pytest
"""
import logging
import os
import urllib
from functools import partial
from typing import Any, Dict, Generator, List, Optional, Sequence

import coolname
import mlflow
import pandas as pd
from mlflow.store.artifact.artifact_repository_registry import (
    _artifact_repository_registry,
)
from mlflow.store.tracking import SEARCH_MAX_RESULTS_DEFAULT
from mlflow.tracking import MlflowClient

from mlfoundry import amplitude, constants
from mlfoundry.artifact.truefoundry_artifact_repo import TruefoundryArtifactRepository
from mlfoundry.enums import ViewType
from mlfoundry.exceptions import MlflowException, MlFoundryException
from mlfoundry.internal_namespace import NAMESPACE
from mlfoundry.mlfoundry_run import MlFoundryRun
from mlfoundry.run_utils import append_path_to_rest_tracking_uri, resolve_tracking_uri
from mlfoundry.session import Session
from mlfoundry.tracking.auth_service import AuthService
from mlfoundry.tracking.truefoundry_rest_store import get_rest_store

logger = logging.getLogger(__name__)


def init_rest_tracking(tracking_uri: str, api_key: Optional[str]):
    """init_rest_tracking.

    Args:
        tracking_uri (str): tracking_uri
        api_key (Optional[str]): api_key
    """
    rest_store = get_rest_store(tracking_uri)
    auth_service = AuthService(auth_server_info=rest_store.get_auth_server_info())

    session = Session(auth_service=auth_service, tracking_uri=tracking_uri)
    session.init_session(api_key)

    artifact_repository = partial(TruefoundryArtifactRepository, rest_store=rest_store)
    _artifact_repository_registry.register("s3", artifact_repository)


def get_client(
    tracking_uri: Optional[str] = None,
    disable_analytics: bool = False,
    api_key: Optional[str] = None,
) -> "MlFoundry":
    """Initializes and returns the mlfoundry client.

    Args:
        tracking_uri (Optional[str], optional): Custom tracking server URL.
            If not passed, by default all the run details are sent to Truefoundry server
            and can be visualized at https://app.truefoundry.com/mlfoundry.
            Tracking server URL can be also configured using the `MLF_HOST`
            environment variable. In case environment variable and argument is passed,
            the URL passed via this argument will take precedence.
        disable_analytics (bool, optional): To turn off usage analytics collection, pass `True`.
            By default, this is set to `False`.
        api_key (Optional[str], optional): API key.
            API key can be found at https://app.truefoundry.com/settings. API key can be
            also configured using the `MLF_API_KEY` environment variable. In case the
            environment variable and argument are passed, the value passed via this argument
            will take precedence.

    Returns:
        MlFoundry: Instance of `MlFoundry` class which represents a `run`.

    Examples:
    ### Get client
    Set the API key using the `MLF_API_KEY` environment variable.
    ```
    export MLF_API_KEY="MY-API_KEY"
    ```

    We can then initialize the client, the API key will be picked up from the
    environment variable.
    ```python
    import mlfoundry

    client = mlfoundry.get_client()
    ```

    ### Get client with API key passed via argument.
    ```python
    import mlfoundry

    API_KEY = "MY-API_KEY"
    client = mlfoundry.get_client(api_key=API_KEY)
    ```
    """
    # TODO (chiragjn): Will potentially need to make MlFoundry (and possibly MlFoundryRun) a Singleton instance.
    #                  Since this sets the tracking URI in global namespace, if someone were to call
    #                  get_client again with different tracking uri, the ongoing run's data will start getting
    #                  pushed to another datastore. Or we should not allow passing in tracking URI and just have
    #                  fixed online and offline clients
    amplitude.init(disable_analytics)
    tracking_uri = resolve_tracking_uri(tracking_uri)
    if tracking_uri.startswith("file:"):
        tracking_uri = os.path.join(tracking_uri, constants.MLRUNS_FOLDER_NAME)
    else:
        tracking_uri = append_path_to_rest_tracking_uri(tracking_uri)
        init_rest_tracking(tracking_uri=tracking_uri, api_key=api_key)
    amplitude.track(
        amplitude.Event.GET_CLIENT,
        # tracking whether user is using file:// or https://
        event_properties={
            "tracking_scheme": urllib.parse.urlparse(tracking_uri).scheme
        },
    )
    return MlFoundry(tracking_uri)


def get_monitoring_client(monitoring_uri: str, model_id: str, model_version: str):
    from mlfoundry.monitoring.store import MonitoringClient

    return MonitoringClient(
        monitoring_uri=monitoring_uri, model_id=model_id, model_version=model_version
    )


class MlFoundry:
    """MlFoundry."""

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
    ):
        """__init__.

        Args:
            tracking_uri (Optional[str], optional): tracking_uri
        """
        try:
            mlflow.set_tracking_uri(tracking_uri)
        except MlflowException as e:
            err_msg = (
                f"Could not initialise mlfoundry object. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e

        self.mlflow_client = MlflowClient()

    def _get_or_create_project(self, project_name: str, owner: Optional[str]) -> str:
        """_get_or_create_experiment.

        Args:
            project_name (str): The name of the project.
            owner (Optional[str], optional): Owner of the project. If owner is not passed,
                the current user will be used as owner. If the given owner
                does not have the project, it will be created under
                the current user.

        Returns:
            str: The id of the project.
        """
        experiment_name = project_name
        try:
            experiment = self.mlflow_client.get_experiment_by_name(
                experiment_name, owner_subject_id=owner
            )
            if experiment is not None:
                return experiment.experiment_id
            if not owner:
                logger.info(
                    f"project {experiment_name} does not exist. Creating {experiment_name}."
                )
                return self.mlflow_client.create_experiment(experiment_name)
            else:
                logger.warning(
                    f"project {experiment_name} under owner {owner} does not exist. "
                    "looking for project under current user."
                )
                return self._get_or_create_project(
                    project_name=project_name, owner=None
                )
        except MlflowException as e:
            err_msg = (
                f"Error happened in creating or getting project based on project name: "
                f"{experiment_name}. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e

    def get_all_projects(self) -> List[str]:
        """Returns a list of project ids accessible by the current user.

        Returns:
            List[str]: A list of project ids.
        """
        amplitude.track(amplitude.Event.GET_ALL_PROJECTS)
        try:
            experiments = self.mlflow_client.list_experiments(view_type=ViewType.ALL)
        except MlflowException as e:
            err_msg = (
                f"Error happened in fetching project names. Error details: {e.message}"
            )
            raise MlFoundryException(err_msg) from e

        projects = []
        for e in experiments:
            # Experiment ID 0 represents default project which we are removing.
            if e.experiment_id != "0":
                projects.append(e.name)

        return projects

    def create_run(
        self,
        project_name: str,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        owner: Optional[str] = None,
        log_system_metrics: bool = True,
        **kwargs,
    ) -> MlFoundryRun:
        """Initialize a `run`.

        In a machine learning experiment `run` represents a single experiment
        conducted under a project.
        Args:
            project_name (str): The name of the project under which the run will be created.
                project_name should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
                The user must have `ADMIN` or `WRITE` access to this project.
            run_name (Optional[str], optional): The name of the run. If not passed, a randomly
                generated name is assigned to the run. Under a project, all runs should have
                a unique name. If the passed `run_name` is already used under a project, the
                `run_name` will be de-duplicated by adding a suffix.
                run name should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
            tags (Optional[Dict[str, Any]], optional): Optional tags to attach with
                this run. Tags are key-value pairs.
            owner (Optional[str], optional): Owner of the project. If owner is not passed,
                the current user will be used as owner. If the given owner
                does not have the project, it will be created under
                the current user.
            log_system_metrics (bool, optional): Automatically collect system metrics. By default, this is
                set to `True`.
            kwargs:

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:
        ### Create a run under current user.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()

        tags = {"model_type": "svm"}
        run = client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel", tags=tags
        )

        run.end()
        ```

        ### Creating a run using context manager.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()
        with client.create_run(
            project_name="my-classification-project", run_name="svm-with-rbf-kernel"
        ) as run:
            # ...
            # Model training code
            ...
        # `run` will be automatically marked as `FINISHED` or `FAILED`.
        ```

        ### Create a run in a project owned by a different user.
        ```python
        import mlfoundry

        client = mlfoundry.get_client()

        tags = {"model_type": "svm"}
        run = client.create_run(
            project_name="my-classification-project",
            run_name="svm-with-rbf-kernel",
            tags=tags,
            owner="bob",
        )
        run.end()
        ```
        """
        amplitude.track(amplitude.Event.CREATE_RUN)
        if not run_name:
            run_name = coolname.generate_slug(2)
            logger.info(
                f"No run_name given. Using a randomly generated name {run_name}."
                " You can pass your own using the `run_name` argument"
            )
        if project_name == "" or (not isinstance(project_name, str)):
            raise MlFoundryException(
                f"project_name must be string type and not empty. "
                f"Got {type(project_name)} type with value {project_name!r}"
            )

        experiment_id = self._get_or_create_project(project_name, owner=owner)

        if tags is not None:
            NAMESPACE.validate_namespace_not_used(tags.keys())
        else:
            tags = {}

        run = self.mlflow_client.create_run(experiment_id, name=run_name, tags=tags)
        mlf_run_id = run.info.run_id

        mlf_run = MlFoundryRun(
            experiment_id, mlf_run_id, log_system_metrics=log_system_metrics, **kwargs
        )
        # TODO(Rizwan): Revisit this once run lifecycle is formalised
        mlf_run._add_git_info()
        mlf_run._add_python_mlf_version()
        logger.info(f"Run {run.info.fqn!r} has started.")
        return mlf_run

    def get_run(self, run_id: str) -> MlFoundryRun:
        """Get an existing `run` by the `run_id`.

        Args:
            run_id (str): run_id or fqn of an existing `run`.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.
        """
        amplitude.track(amplitude.Event.GET_RUN)
        if run_id == "" or (not isinstance(run_id, str)):
            raise MlFoundryException(
                f"run_id must be string type and not empty. "
                f"Got {type(run_id)} type with value {run_id}"
            )
        if "/" in run_id:
            return self.get_run_by_fqn(run_id)

        run = self.mlflow_client.get_run(run_id)
        return MlFoundryRun(
            experiment_id=run.info.experiment_id,
            run_id=run.info.run_id,
            log_system_metrics=False,
        )

    def get_run_by_fqn(self, run_fqn: str) -> MlFoundryRun:
        """Get an existing `run` by `fqn`.

        `fqn` stands for Fully Qualified Name. A run `fqn` has the following pattern:
        owner/project_name/run_name

        If user `bob` has created a run `svm` under the project `cat-classifier`,
        the `fqn` will be `bob/cat-classifier/svm`.

        Args:
            run_fqn (str): `fqn` of an existing run.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.
        """
        run = self.mlflow_client.get_run_by_fqn(run_fqn)
        return MlFoundryRun(
            experiment_id=run.info.experiment_id,
            run_id=run.info.run_id,
            log_system_metrics=False,
        )

    def get_all_runs(
        self, project_name: str, owner: Optional[str] = None
    ) -> pd.DataFrame:
        """Returns all the run name and id present under a project.

        The user must have `READ` access to the project.
        Args:
            project_name (str): Name of the project.
            owner (Optional[str], optional): Owner of the project. If owner is not passed,
                                   the current user will be used as owner.
        Returns:
            pd.DataFrame: dataframe with two columns- run_id and run_name
        """
        amplitude.track(amplitude.Event.GET_ALL_RUNS)
        if project_name == "" or (not isinstance(project_name, str)):
            raise MlFoundryException(
                f"project_name must be string type and not empty. "
                f"Got {type(project_name)} type with value {project_name}"
            )
        experiment = self.mlflow_client.get_experiment_by_name(
            project_name, owner_subject_id=owner
        )
        if experiment is None:
            return pd.DataFrame(
                columns=[constants.RUN_ID_COL_NAME, constants.RUN_NAME_COL_NAME]
            )

        experiment_id = experiment.experiment_id

        try:
            all_run_infos = self.mlflow_client.list_run_infos(
                experiment_id, run_view_type=ViewType.ALL
            )
        except MlflowException as e:
            err_msg = f"Error happened in while fetching runs for project {project_name}. Error details: {e.message}"
            raise MlFoundryException(err_msg) from e

        runs = []

        for run_info in all_run_infos:
            try:
                run = self.mlflow_client.get_run(run_info.run_id)
                run_name = run.info.name or run.data.tags.get(
                    constants.RUN_NAME_COL_NAME, ""
                )
                runs.append((run_info.run_id, run_name))
            except MlflowException as e:
                logger.warning(
                    f"Could not fetch details of run with run_id {run_info.run_id}. "
                    f"Skipping this one. Error details: {e.message}. "
                )

        return pd.DataFrame(
            runs, columns=[constants.RUN_ID_COL_NAME, constants.RUN_NAME_COL_NAME]
        )

    def search_runs(
        self,
        project_name: str,
        filter_string: str = "",
        run_view_type: str = "ACTIVE_ONLY",
        order_by: Sequence[str] = ("attribute.start_time DESC",),
        owner: Optional[str] = None,
    ) -> Generator[MlFoundryRun, None, None]:
        """
        The user must have `READ` access to the project.
        Returns an Generator that returns a MLFoundryRun on each next call.
        All the runs under a project which matches the filter string and the run_view_type are returned.

        Args:
            project_name (str): Name of the project.
            filter_string (str, optional):
                Filter query string, defaults to searching all runs. Identifier required in the LHS of a search expression.
                Signifies an entity to compare against. An identifier has two parts separated by a period: the type of the entity and the name of the entity.
                The type of the entity is metrics, params, attributes, or tags. The entity name can contain alphanumeric characters and special characters.
                You can search using two run attributes : status and artifact_uri. Both attributes have string values.
                When a metric, parameter, or tag name contains a special character like hyphen, space, period, and so on,
                enclose the entity name in double quotes or backticks, params."model-type" or params.`model-type`

            run_view_type (str, optional): one of the following values "ACTIVE_ONLY", "DELETED_ONLY", or "ALL" runs.
            order_by (List[str], optional):
                List of columns to order by (e.g., "metrics.rmse"). Currently supported values
                are metric.key, parameter.key, tag.key, attribute.key. The ``order_by`` column
                can contain an optional ``DESC`` or ``ASC`` value. The default is ``ASC``.
                The default ordering is to sort by ``start_time DESC``.
            owner (Optional[str], optional):
                Owner of the project. If owner is not passed, the current user will be used as owner.

        Examples:
            ```python
            import mlfoundry as mlf

            client = mlf.get_client()
            with client.create_run(project_name="my-project", run_name="run-1") as run1:
                run1.log_metrics(metric_dict={"accuracy": 0.74, "loss": 0.6})
                run1.log_params({"model": "LogisticRegression", "lambda": "0.001"})

            with client.create_run(project_name="my-project", run_name="run-2") as run2:
                run2.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4})
                run2.log_params({"model": "SVM"})

            # Search for the subset of runs with logged accuracy metric greater than 0.75
            filter_string = "metrics.accuracy > 0.75"
            runs = client.search_runs(project_name="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7
            filter_string = "metrics.accuracy > 0.7"
            runs = client.search_runs(project_name="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7 and model="LogisticRegression"
            filter_string = "metrics.accuracy > 0.7 and params.model = 'LogisticRegression'"
            runs = client.search_runs(project_name="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7 and order by accuracy in Descending  order
            filter_string = "metrics.accuracy > 0.7"
            order_by = ["metric.accuracy DESC"]
            runs = client.search_runs(
                project_name="my-project", filter_string=filter_string, order_by=order_by
            )

            ```

        Returns:
            Genarator[MlFoundryRun, None, None]: MLFoundryRuns matching the search query.
        """
        if project_name == "" or (not isinstance(project_name, str)):
            raise MlFoundryException(
                f"project_name must be string type and not empty. "
                f"Got {type(project_name)} type with value {project_name!r}"
            )
        try:
            run_view_type = ViewType.from_string(run_view_type.lower())
        except Exception as e:
            raise MlFoundryException(e) from e

        try:
            experiment = self.mlflow_client.get_experiment_by_name(
                project_name, owner_subject_id=owner
            )
        except MlflowException as e:
            raise MlFoundryException(e) from e  # user doesnot have READ permission

        if experiment is None:
            owner = f"owner - {owner}" if owner is not None else "current user"
            logger.warning(
                f"Project with name {project_name} does not exist under the {owner}."
            )
            return

        experiment_id = experiment.experiment_id

        page_token = None
        done = False
        while not done:
            all_runs = self.mlflow_client.search_runs(
                experiment_ids=[experiment_id],
                filter_string=filter_string,
                run_view_type=run_view_type,
                max_results=SEARCH_MAX_RESULTS_DEFAULT,
                order_by=order_by,
                page_token=page_token,
            )
            page_token = all_runs.token
            for run in all_runs:
                yield MlFoundryRun(
                    run.info.experiment_id, run.info.run_id, log_system_metrics=False
                )
            done = page_token is None

    @staticmethod
    def get_tracking_uri():
        """get_tracking_uri."""
        return mlflow.tracking.get_tracking_uri()
