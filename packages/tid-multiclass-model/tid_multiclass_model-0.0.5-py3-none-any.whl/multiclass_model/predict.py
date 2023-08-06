import typing as t

import numpy as np
import pandas as pd

from multiclass_model import __version__ as _version
from multiclass_model.config.core import config
from multiclass_model.processing.data_manager import load_pipeline

pipeline_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
_classification_pipe = load_pipeline(file_name=pipeline_file_name)


def make_prediction(input_data: pd.DataFrame) -> dict:

    data = pd.DataFrame(input_data)
    results = {"predictions": None, "version": _version, }

    predictions = _classification_pipe.predict(data)

    results = {
        "predictions": [int(y_hat) for y_hat in predictions],  # type: ignore
        "version": _version,
    }

    return results
