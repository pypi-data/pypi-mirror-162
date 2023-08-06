from config.core import config
from processing.data_manager import load_dataset, save_pipeline, save_dataset
from sklearn.model_selection import train_test_split
from pipeline import transformer, pipe, three_transformers


def run_training() -> None:
    """Training the model."""

    # read training data
    data = load_dataset(file_name = config.app_config.whole_data_file)
    data = transformer.fit_transform(data)

    # divide the train and test set
    X_train, X_test, y_train, y_test = train_test_split(data[config.model_config.features],
                                                        data[config.model_config.target],
                                                        test_size = config.model_config.test_size,
                                                        random_state = config.model_config.random_state,
                                                        stratify = data[config.model_config.target])
    X_train, X_test = X_train.copy(), X_test.copy()

    dictDF = {'train': X_train, 'y_train': y_train, 'test': X_test}
    save_dataset(**dictDF)

    # fit the model
    pipe.fit(X_train, y_train)

    # persist the model
    save_pipeline(pipeline_to_persist = pipe)


if __name__ == '__main__':
    run_training()