import enum
import posixpath
import sys
from typing import Union
from uuid import uuid4

from mlflow.entities import RunLog
from pydantic import BaseModel

from mlfoundry.constants import RUN_LOGS_DIR
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.log_types.pydantic_base import PydanticBase
from mlfoundry.log_types.utils import save_artifact_helper, validate_key_name

PLOT_LOG_DIR = posixpath.join(RUN_LOGS_DIR, "plots")

PlotObjType = Union[
    "matplotlib.figure.Figure",
    "plotly.graph_objects.Figure",
    "matplotlib.pyplot",
]


@enum.unique
class Format(enum.Enum):
    SVG = "SVG"
    HTML = "HTML"
    PNG = "PNG"


def _is_matplotlib_figure(fig) -> bool:
    if "matplotlib" not in sys.modules:
        return False
    import matplotlib

    return isinstance(fig, matplotlib.figure.Figure)


def _is_matplotlib_plt(plt) -> bool:
    if "matplotlib" not in sys.modules:
        return False
    return getattr(plt, "__name__", "") == "matplotlib.pyplot"


def _is_plotly_figure(fig) -> bool:
    if "plotly" not in sys.modules:
        return False

    import plotly

    return isinstance(fig, plotly.graph_objects.Figure)


def get_plot_file_name(key: str, step: int, format: Format) -> str:
    return f"{key}-{step}-{uuid4()}.{format.value.lower()}"


class PlotArtifact(BaseModel):
    artifact_path: str
    format: Format

    class Config:
        allow_mutation = False
        use_enum_values = True


def _save_matplotlib_figure(
    figure: "matplotlib.figure.Figure",
    run: "mlfoundry.MlFoundryRun",
    key: str,
    step: int,
) -> PlotArtifact:
    supported_formats = figure.canvas.get_supported_filetypes().keys()
    if "svg" in supported_formats:
        format_ = Format.SVG
    elif "png" in supported_formats:
        format_ = Format.PNG
    else:
        raise MlFoundryException(
            f"Could not save {key} {figure} matplotlib figure"
            "in either SVG or PNG format"
        )
    file_path = get_plot_file_name(key=key, step=step, format=format_)
    artifact_path = posixpath.join(PLOT_LOG_DIR, file_path)
    with save_artifact_helper(run, artifact_path=artifact_path) as local_path:
        figure.savefig(local_path)
    return PlotArtifact(artifact_path=artifact_path, format=format_)


def _save_matplotlib_plt(
    plt: "matplotlib.pyplot",
    run: "mlfoundry.MlFoundryRun",
    key: str,
    step: int,
) -> PlotArtifact:
    figure = plt.gcf()
    return _save_matplotlib_figure(figure=figure, run=run, key=key, step=step)


def _save_plotly_figure(
    figure: "plotly.graph_objects.Figure",
    run: "mlfoundry.MlFoundryRun",
    key: str,
    step: int,
) -> PlotArtifact:
    format_ = Format.HTML
    file_path = get_plot_file_name(key=key, step=step, format=format_)
    artifact_path = posixpath.join(PLOT_LOG_DIR, file_path)
    with save_artifact_helper(run, artifact_path=artifact_path) as local_path:
        figure.write_html(local_path, include_plotlyjs="cdn", auto_open=False)
    return PlotArtifact(artifact_path=artifact_path, format=format_)


class Plot:
    def __init__(self, plot_obj: PlotObjType):
        self._plot_obj = plot_obj

    def _save_plot(
        self, run: "mlfoundry.MlFoundryRun", key: str, step: int
    ) -> PlotArtifact:
        if _is_matplotlib_plt(self._plot_obj):
            return _save_matplotlib_plt(plt=self._plot_obj, run=run, key=key, step=step)

        if _is_matplotlib_figure(self._plot_obj):
            return _save_matplotlib_figure(
                figure=self._plot_obj, run=run, key=key, step=step
            )

        if _is_plotly_figure(self._plot_obj):
            return _save_plotly_figure(
                figure=self._plot_obj, run=run, key=key, step=step
            )

        raise MlFoundryException(
            f"Unknown type: {type(self._plot_obj)}"
            "Supported types are, matplotlib.figure.Figure, matplotlib.pyplot"
            " and plotly.graph_objects.Figure"
        )

    def to_run_log(
        self,
        run: "mlfoundry.MlFoundryRun",
        key: str,
        step: int = 0,
    ) -> RunLog:
        validate_key_name(key)

        return PlotRunLogType(
            value=self._save_plot(run=run, key=key, step=step)
        ).to_run_log(key=key, step=step)

    def save(
        self,
        run: "mlfoundry.MlFoundryRun",
        key: str,
        step: int = 0,
    ):
        run_log = self.to_run_log(
            run=run,
            key=key,
            step=step,
        )
        run.mlflow_client.insert_run_logs(run_uuid=run.run_id, run_logs=[run_log])


class PlotRunLogType(PydanticBase):
    value: PlotArtifact

    @staticmethod
    def get_log_type() -> str:
        return "plot"


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    import plotly.express as px

    import mlfoundry

    client = mlfoundry.get_client("https://app.devtest.truefoundry.tech")
    # client = mlfoundry.get_client("http://localhost:5000")

    run = client.create_run(project_name="plot-test")

    df = px.data.iris()
    fig = px.scatter(
        df,
        x="sepal_width",
        y="sepal_length",
        color="species",
        size="petal_length",
        hover_data=["petal_width"],
    )
    Plot(fig).save(run, "foo")

    df = px.data.tips()
    fig = px.histogram(
        df,
        x="total_bill",
        y="tip",
        color="sex",
        marginal="rug",
        hover_data=df.columns,
    )
    Plot(fig).save(run, "foo", step=1)

    names = ["group_a", "group_b", "group_c"]
    values = [1, 10, 100]
    plt.figure(figsize=(9, 3))
    plt.subplot(131)
    plt.bar(names, values)
    plt.subplot(132)
    plt.scatter(names, values)
    plt.subplot(133)
    plt.plot(names, values)
    plt.suptitle("Categorical Plotting")

    Plot(plt).save(run, "bar")

    plt.clf()

    data = {
        "a": np.arange(50),
        "c": np.random.randint(0, 50, 50),
        "d": np.random.randn(50),
    }
    data["b"] = data["a"] + 10 * np.random.randn(50)
    data["d"] = np.abs(data["d"]) * 100
    plt.scatter("a", "b", c="c", s="d", data=data)
    plt.xlabel("entry a")
    plt.ylabel("entry b")
    Plot(plt).save(run, "bar", 2)

    plt.clf()

    ax = plt.subplot()
    t = np.arange(0.0, 5.0, 0.01)
    s = np.cos(2 * np.pi * t)
    (line,) = plt.plot(t, s, lw=2)

    plt.annotate(
        "local max",
        xy=(2, 1),
        xytext=(3, 1.5),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    plt.ylim(-2, 2)
    Plot(plt.gcf()).save(run, "bar", 3)
