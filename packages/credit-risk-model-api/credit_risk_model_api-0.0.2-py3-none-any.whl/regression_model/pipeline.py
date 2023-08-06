from regression_model.pipeline_processors.transformers_dependencies import *
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from regression_model.config.core import config
# from regression_model.processing.data_manager import load_optimized_parameters

# json_file_name = f"{config.app_config.paramter_saved_file}"
# json_paramters = load_optimized_parameters(file_name = json_file_name)

json_paramters = {'warm_start': False,
 'verbose': 0,
 'tol': 1e-05,
 'solver': 'lbfgs',
 'random_state': None,
 'penalty': 'l2',
 'multi_class': 'auto',
 'max_iter': 100.0,
 'intercept_scaling': 1,
 'fit_intercept': True,
 'dual': False,
 'class_weight': 'imbalanced',
 'C': 0.1}


transformer = Pipeline([
    ('data_cleansing', DataCleansing()),
    ('targetVariablePreprocess', TargetVariablePreprocess()),
    ('convertTargetToBinary', ConvertTargetToBinary())
])



two_transformers = Pipeline([
    ('preprocess', Preprocess()),
    ('preprocessNumericVariables', PreprocessNumericVariables())
    # ('dummy_transformer', DummyTransformer(columns_list = config.model_config.selected_names))
])


three_transformers = Pipeline([
    ('preprocess', Preprocess()),
    ('preprocessNumericVariables', PreprocessNumericVariables()),
    ('dummy_transformer', DummyTransformer(columns_list = config.model_config.selected_names))
])


pipe = Pipeline([
    ('preprocess', Preprocess()),
    ('preprocessNumericVariables', PreprocessNumericVariables()),
    ('dummy_transformer', DummyTransformer(columns_list = config.model_config.selected_names)),
    ('logistic_Reg', LogisticRegression(**json_paramters))
])