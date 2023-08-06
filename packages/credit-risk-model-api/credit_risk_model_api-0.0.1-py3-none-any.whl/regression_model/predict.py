import typing as t

from regression_model.config.core import config
import pandas as pd
from regression_model.processing.data_manager import load_pipeline
from regression_model.processing.validation import validate_inputs
from regression_model import __version__ as _version
from regression_model.pipeline import three_transformers

pipeline_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
_pipe = load_pipeline(file_name = pipeline_file_name)



def make_prediction(*, input_data: t.Union[pd.DataFrame, dict]) -> dict:
    """Make a prediction using a saved model pipeline."""

    data = pd.DataFrame(input_data)
    validated_data, errors = validate_inputs(input_data = data)
    results = {"predictions": None, "proba_predictions": None, "version": _version, "errors": errors}

    # print(validated_data[config.model_config.features])
    # print(_pipe)
    # validated_data[config.model_config.features] = three_transformers.fit_transform(validated_data[config.model_config.features])
    # validated_data = three_transformers.transform(validated_data[config.model_config.features])
    # validated_data = _pipe.predict(X = validated_data)


    if not errors:
        predictions = _pipe.predict(X = validated_data)
        proba_predictions = _pipe.predict_proba(X = validated_data)[:][: , 1]



        results = {
            "predictions": predictions,
            "proba_predictions": proba_predictions,
            "version": _version,
            "errors": errors
            }

    return results
