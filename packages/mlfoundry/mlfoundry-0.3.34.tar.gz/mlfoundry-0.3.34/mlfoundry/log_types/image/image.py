import os
import posixpath
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

from mlflow.entities import RunLog

from mlfoundry.exceptions import MlFoundryException
from mlfoundry.log_types.image.constants import (
    DEFAULT_IMAGE_FORMAT,
    IMAGE_KEY_REGEX,
    IMAGE_LOG_DIR,
    MEDIA_DIR,
    MISSING_PILLOW_PACKAGE_MESSAGE,
)
from mlfoundry.log_types.image.image_normalizer import normalize_image
from mlfoundry.log_types.image.types import BoundingBoxGroups, ClassGroups
from mlfoundry.log_types.pydantic_base import PydanticBase
from mlfoundry.run_utils import get_module

DataOrPathType = Union[str, Path, "numpy.ndarray", "PIL.Image.Image"]
ClassGroupsType = Dict[str, Union[str, List[str]]]
BBoxGrouptype = Dict[str, List[Dict]]


def validate_key_name(key: str):
    if not key or not IMAGE_KEY_REGEX.match(key):
        raise MlFoundryException(
            f"Invalid run image key: {key} should only contain alphanumeric, hyphen or underscore"
        )


def get_run_log_file_name(key: str, step: int):
    return f"{key}-{step}-{uuid4()}.json"


class Image:
    def __init__(
        self,
        data_or_path: DataOrPathType,
        caption: Optional[str] = None,
        class_groups: Optional[ClassGroupsType] = None,
        bbox_groups: Optional[BBoxGrouptype] = None,
    ):
        """Represent and log image using this class in `mlfoundry`.

        You can initialize `mlfoundry.Image` by either by using a local path
        or you can use a numpy array / PIL.Image object.

        If you are using numpy array, we only support the following data types,
        - bool
        - integer [0 - 255]
        - unsigned integer [0 - 255]
        - float [0.0 - 1.0]

        Any out of range value will be clipped.

        As for array shape/dim, we follow the following structures,
        - H x W (Grayscale)
        - H x W x 1 (Grayscale)
        - H x W x 3 (an RGB channel order is assumed)
        - H x W x 4 (an RGBA channel order is assumed)

        `PIL` package is required to log images. To install the `PIL` package,
        run `pip install pillow`.

        We can also log class names and bounding boxes associated with the image.
        Class names and bounding boxes should be always grouped under `actuals` or
        `predictions`. For example, if we have an image where the ground truth class
        is "cat" and predicted class is "dog", we can represent it like,

        ```python
        mlfoundry.Image(
            data_or_path=imarray,
            class_groups={"actuals": "dog", "predictions": "cat"}
        )
        ```

        You can define a bounding box using the following dictionary structure,
        ```python
        {
            "position": {"min_x": 15, "min_y": 5, "max_x": 20, "max_y": 30}, # required, defines the position of the bounding box
                                                                             # (min_x, min_y) defines the top left and
                                                                             # (max_x, max_y) defines the bottom right corner of the box.
            "class_name": "dog", # required, the class name of the bounding box
            "caption": "dog", # optional, the caption of the bounding box.
                              # If not passed, the class name is set as caption.
        }
        ```

        Args:
            data_or_path (Union[str, Path, "numpy.ndarray", "PIL.Image.Image"]):
                Either the local path or the image object (Numpy array or PIL Image).
            caption (Optional[str], optional): A string caption or label for the image.
            class_groups (Optional[Dict[str, Union[str, List[str]]]], optional):
                Class names associated with the image. Expects class name(s) grouped by
                `predictions` or `actuals`.
            bbox_groups (Optional[Dict[str, List[Dict]]], optional): Bounding boxes
                associated with the image. Expects bounding boxes grouped by `predictions`
                or `actuals`.

        Examples:
        ### Logging images with caption and class names

        ```python
        import mlfoundry
        import numpy as np

        client = mlfoundry.get_client()
        run = client.create_run(
            project_name="my-classification-project",
        )

        imarray = np.random.randint(low=0, high=256, size=(100, 100, 3))

        images_to_log = {
            "logged-image-array": mlfoundry.Image(
                data_or_path=imarray,
                caption="testing image logging",
                class_groups={"actuals": "dog", "predictions": "cat"},
            ),
        }
        run.log_images(images_to_log, step=1)

        run.end()
        ```

        ### Logging images for a multi-label classification problem

        ```python
        images_to_log = {
            "logged-image-array": mlfoundry.Image(
                data_or_path=imarray,
                caption="testing image logging",
                class_groups={"actuals": ["dog", "human"], "predictions": ["cat", "human"]},
            ),
        }

        run.log_images(images_to_log, step=1)
        ```

        ### Logging images with bounding boxes

        ```python
        images_to_log = {
            "logged-image-array": mlfoundry.Image(
                data_or_path=imarray,
                caption="testing image logging",
                bbox_groups={
                    "predictions": [
                        {
                            "position": {"min_x": 5, "min_y": 5, "max_x": 20, "max_y": 30},
                            "class_name": "cat",
                        }
                    ],
                    "actuals": [
                        {
                            "position": {"min_x": 15, "min_y": 5, "max_x": 20, "max_y": 30},
                            "class_name": "dog",
                            "caption": "dog",
                        }
                    ],
                },
            ),
        }

        run.log_images(images_to_log, step=1)
        ```
        """
        self._run = None

        self._caption = None
        self._class_groups = None
        self._bbox_groups = None

        self._image = None
        self._image_artifact_path = None
        self._local_image_path = None

        self._init_image(data_or_path)
        self._init_metadata(
            caption=caption, class_groups=class_groups, bbox_groups=bbox_groups
        )

    @property
    def image(self) -> "PIL.Image.Image":
        if self._image is None:
            raise MlFoundryException("Image is not initialized")
        return self._image

    @property
    def caption(self) -> Optional[str]:
        return self._caption

    @property
    def class_groups(self) -> Optional[ClassGroups]:
        return self._class_groups

    @property
    def bbox_groups(self) -> Optional[BoundingBoxGroups]:
        return self._bbox_groups

    @property
    def run(self) -> "mlfoundry.MlFoundryRun":
        if self._run is None:
            raise MlFoundryException("Image is not bound to a run yet.")
        return self._run

    @property
    def image_artifact_path(self) -> str:
        if self._image_artifact_path is not None:
            return self._image_artifact_path

        if self._local_image_path is None:
            image_artifact_path = self._serialize_and_save_image_as_artifact()
        else:
            image_artifact_path = self._copy_local_image_as_artifact()

        self._image_artifact_path = image_artifact_path
        return self._image_artifact_path

    def _serialize_and_save_image_as_artifact(
        self, artifact_path: str = MEDIA_DIR
    ) -> str:
        file_name = f"{uuid4()}.{DEFAULT_IMAGE_FORMAT}"
        image_artifact_path = posixpath.join(artifact_path, file_name)
        with tempfile.TemporaryDirectory() as local_dir:
            local_path = os.path.join(local_dir, file_name)
            self.image.save(local_path)
            self.run.mlflow_client.log_artifact(
                run_id=self.run.run_id,
                local_path=local_path,
                artifact_path=artifact_path,
            )
        return image_artifact_path

    def _copy_local_image_as_artifact(self, artifact_path: str = MEDIA_DIR) -> str:
        file_name = os.path.basename(self._local_image_path)
        new_file_name = f"{uuid4()}-{file_name}"
        image_artifact_path = posixpath.join(artifact_path, new_file_name)
        with tempfile.TemporaryDirectory() as local_dir:
            new_local_image_path = os.path.join(local_dir, new_file_name)
            shutil.copy2(self._local_image_path, new_local_image_path)
            self.run.mlflow_client.log_artifact(
                run_id=self.run.run_id,
                local_path=new_local_image_path,
                artifact_path=artifact_path,
            )
        return image_artifact_path

    def _bind_to_run(self, run: "mlfoundry.MlFoundryRun"):
        if self._run is None:
            self._run = run
            return
        if self._run.run_id != run.run_id:
            raise MlFoundryException(
                f"Image is already bound to run {self._run.run_id}"
            )

    def _init_image(self, data_or_path: DataOrPathType):
        pil_image_module = get_module(
            module_name="PIL.Image",
            required=True,
            error_message=MISSING_PILLOW_PACKAGE_MESSAGE,
        )
        if isinstance(data_or_path, (str, Path)):
            self._local_image_path = os.path.abspath(data_or_path)
            with pil_image_module.open(data_or_path) as image:
                image.load()
                self._image = image
        else:
            self._image = normalize_image(data_or_path)

    def _init_metadata(
        self,
        caption: Optional[str],
        class_groups: Optional[ClassGroupsType],
        bbox_groups: Optional[Dict],
    ):
        if caption is not None:
            self._caption = str(caption)

        if class_groups:
            self._class_groups = ClassGroups.parse_obj(class_groups)

        if bbox_groups:
            self._bbox_groups = BoundingBoxGroups.parse_obj(bbox_groups)

    def _to_dict(self) -> Dict:
        dict_ = {}
        dict_["caption"] = self._caption
        dict_["image_artifact_path"] = self.image_artifact_path
        dict_["class_groups"] = (
            self.class_groups.to_dict() if self.class_groups is not None else None
        )
        dict_["bbox_groups"] = (
            self.bbox_groups.to_dict() if self.bbox_groups is not None else None
        )

        return dict_

    def to_run_log(
        self,
        run: "mlfoundry.MlFoundryRun",
        key: str,
        step: int = 0,
        timestamp: Optional[int] = None,
    ) -> RunLog:
        validate_key_name(key)

        self._bind_to_run(run)

        return ImageRunLogType(value=self._to_dict()).to_run_log_as_artifact(
            key=key,
            run_id=self.run.run_id,
            mlflow_client=self.run.mlflow_client,
            file_name=get_run_log_file_name(key=key, step=step),
            artifact_path=IMAGE_LOG_DIR,
            step=step,
            timestamp=timestamp,
        )

    def save(
        self,
        run: "mlfoundry.MlFoundryRun",
        key: str,
        step: int = 0,
        timestamp: Optional[int] = None,
    ):
        run_log = self.to_run_log(
            run=run,
            key=key,
            step=step,
            timestamp=timestamp,
        )
        self.run.mlflow_client.insert_run_logs(
            run_uuid=self.run.run_id, run_logs=[run_log]
        )


class ImageRunLogType(PydanticBase):
    value: Dict

    @staticmethod
    def get_log_type() -> str:
        return "image"
