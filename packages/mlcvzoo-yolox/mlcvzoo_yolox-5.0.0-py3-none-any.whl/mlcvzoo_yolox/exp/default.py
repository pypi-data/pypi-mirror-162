from enum import auto
from typing import Any, Dict, NamedTuple, Type

try:
    # python3.10
    from enum import StrEnum  # type: ignore
except ImportError:
    from backports.strenum import StrEnum

from yolox.exp import Exp as YOLOXBaseExp

from mlcvzoo_yolox.third_party.yolox.exps.yolox_nano import Exp as YOLOXNanoExp


class YOLOXExperiments(StrEnum):
    NANO = auto()
    TINY = auto()
    S = auto()
    M = auto()
    L = auto()
    X = auto()


class YOLOXSettingsTuple(NamedTuple):

    constructor: Type[YOLOXBaseExp]
    attribute_dict: Dict[str, Any]


yolox_experiment_settings: Dict[str, YOLOXSettingsTuple] = {
    YOLOXExperiments.NANO.upper(): YOLOXSettingsTuple(  # type: ignore
        constructor=YOLOXNanoExp, attribute_dict={}  # everything as in default
    ),
    YOLOXExperiments.TINY.upper(): YOLOXSettingsTuple(  # type: ignore
        constructor=YOLOXBaseExp,
        attribute_dict={
            "depth": 0.33,
            "width": 0.375,
            "input_size": (416, 416),
            "mosaic_scale": (0.5, 1.5),
            "random_size": (10, 20),
            "test_size": (416, 416),
            "enable_mixup": False,
        },
    ),
    YOLOXExperiments.S.upper(): YOLOXSettingsTuple(  # type: ignore
        constructor=YOLOXBaseExp, attribute_dict={"depth": 0.33, "width": 0.5}
    ),
    YOLOXExperiments.M.upper(): YOLOXSettingsTuple(  # type: ignore
        constructor=YOLOXBaseExp, attribute_dict={"depth": 0.67, "width": 0.75}
    ),
    YOLOXExperiments.L.upper(): YOLOXSettingsTuple(  # type: ignore
        constructor=YOLOXBaseExp, attribute_dict={}  # everything as in default
    ),
    YOLOXExperiments.X.upper(): YOLOXSettingsTuple(  # type: ignore
        constructor=YOLOXBaseExp, attribute_dict={"depth": 1.33, "width": 1.25}
    ),
}
