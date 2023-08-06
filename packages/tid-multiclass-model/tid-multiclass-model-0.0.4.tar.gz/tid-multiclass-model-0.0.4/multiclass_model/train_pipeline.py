import numpy as np
from config.core import config
from pipeline import category_prediction_pipeline
from processing.data_manager import load_dataset, save_pipeline
from sklearn.model_selection import train_test_split
from multiclass_model.custom_functions import custom_functions as cf
from processing.data_manager import load_json

def run_training() -> None:
    """Train the model."""

    # read training data
    data = load_dataset(file_name=config.app_config.training_data_file)
    map_target = load_json(file_name=config.app_config.json_file_target)

    ## to get numerical labels for the target
    data['Map_Product_Category'] = data.Product_Category.map(map_target)

    # divide train and test
    X_train, X_test, y_train, y_test = train_test_split(
        data[config.model_config.initial_features],  # predictors
        data[config.model_config.target],
        test_size=config.model_config.test_size,
        random_state=config.model_config.random_state,
    )
    X_train = cf.splitter(data = X_train)

    # fit model
    category_prediction_pipeline.fit(X_train, y_train)

    # persist trained model
    save_pipeline(pipeline_to_persist=category_prediction_pipeline)


if __name__ == "__main__":
    run_training()
