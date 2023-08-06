import logging
import typing
from datetime import datetime

from pydantic import BaseModel, Field, constr

logger = logging.getLogger(__name__)

# TODO @nikp1172 Add support for np types https://numpy.org/doc/stable/user/basics.types.html
EntityValue = typing.Union[str, int, float]


class PredictionData(BaseModel):
    value: EntityValue
    probabilities: typing.Dict[str, float] = Field(default_factory=dict)
    shap_values: typing.Dict[str, float] = Field(default_factory=dict)

    class Config:
        smart_union = True


class BasePacket(BaseModel):
    class Config:
        smart_union = True


class Prediction(BaseModel):

    data_id: constr(min_length=1, max_length=64)
    features: typing.Dict[str, EntityValue]
    prediction_data: PredictionData

    raw_data: typing.Optional[typing.Dict] = Field(default_factory=dict)
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.utcnow().replace(tzinfo=None)
    )

    class Config:
        smart_union = True


class PredictionPacket(BasePacket):
    model_id: constr(min_length=1, max_length=64)
    model_version: constr(min_length=1, max_length=128)
    dataset_id: constr(min_length=1, max_length=64)

    prediction: Prediction


class Actual(BaseModel):
    data_id: constr(min_length=1, max_length=64)
    value: EntityValue

    class Config:
        smart_union = True


class ActualPacket(BasePacket):
    model_id: constr(min_length=1, max_length=64)
    model_version: constr(min_length=1, max_length=128)
    dataset_id: constr(min_length=1, max_length=64)

    actual: Actual
