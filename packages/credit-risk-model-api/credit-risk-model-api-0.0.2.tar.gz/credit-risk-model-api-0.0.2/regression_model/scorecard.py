import typing as t
import pandas as pd
import numpy as np

from sklearn.metrics import roc_curve
from regression_model.config.core import config
from regression_model.processing.data_manager import load_pipeline, load_dataset
from regression_model.processing.validation import validate_inputs
from regression_model import __version__ as _version
from regression_model.pipeline import transformer, three_transformers


pipeline_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
_pipe = load_pipeline(file_name = pipeline_file_name)
y_train = load_dataset(file_name = config.app_config.target_data_file)
# print(y_train)

# best_thresh = 0.429246

def get_missing_values(selected_names):
    missing_list = []
    for item in selected_names:
        missing_list.append(item + ':missing')
    return missing_list


def computeApprovalRejectionRate(df, section, best_thresh, max_score, min_score, max_sum_coef, min_sum_coef):
    def n_approved(p):
        return np.where(df[f'y_hat_{section}_proba'] >= p, 1, 0).sum()
    df_cutoffs = pd.DataFrame([best_thresh], columns = ['best_thresh'])
    df_cutoffs['Cut-Off Score'] = ((np.log(df_cutoffs['best_thresh'] / (1 - df_cutoffs['best_thresh'])) - min_sum_coef) *
                                    ((max_score - min_score) / (max_sum_coef - min_sum_coef)) + min_score).round()
    df_cutoffs['N Approved'] = df_cutoffs['best_thresh'].apply(n_approved)
    df_cutoffs['N Rejected'] = df[f'y_hat_{section}_proba'].shape[0] - df_cutoffs['N Approved']
    # df_cutoffs['Approval Rate'] = df_cutoffs['N Approved'] / df[f'y_hat_{section}_proba'].shape[0]
    df_cutoffs['Approval Rate'] = df_cutoffs['N Approved'] / (float(df_cutoffs['N Approved']) + float(df_cutoffs['N Rejected']))
    df_cutoffs['Rejection Rate'] = 1 - df_cutoffs['Approval Rate']
    return df_cutoffs


# def generate_scorecard(*, input_data: t.Union[pd.DataFrame, dict]) -> dict:
def scorecard(data) -> tuple:
    """Generate scorecard using the saved model."""

    # Define the min and max threshholds for our scorecard
    min_score = 300
    max_score = 850

    # data = load_dataset(file_name = config.app_config.training_data_file)
    validated_data, errors = validate_inputs(input_data = data)
    results = {"predictions": None, "proba_predictions": None, "version": _version, "errors": errors}

    if not errors:
        proba_predictions = _pipe.predict_proba(X = validated_data)[:][: , 1] # use make_prediction instead
        transformed_data = three_transformers.fit_transform(validated_data)
        proba_predictions = pd.DataFrame(proba_predictions, columns = ['y_hat_train_proba'])

        y_train_temp = y_train.copy()
        y_train_temp.reset_index(drop = True, inplace = True)
        proba_predictions = pd.concat([y_train_temp, proba_predictions], axis = 1)
        proba_predictions.columns = ['y_train_class_actual', 'y_hat_train_proba']
        fpr, tpr, thresholds = roc_curve(proba_predictions['y_train_class_actual'], proba_predictions['y_hat_train_proba'])
        # Calculate Youden's J-Statistic to identify the best threshhold
        J = tpr - fpr
        # locate the index of the largest J
        ix = np.argmax(J)
        best_thresh = thresholds[ix]
        # print('Best Threshold: %f' % (best_thresh))

        summary_table = pd.DataFrame(columns = ['Feature name'], data = transformed_data.columns.values)
        summary_table['Coefficients'] = np.transpose(_pipe['logistic_Reg'].coef_)
        summary_table.index = summary_table.index + 1
        summary_table.loc[0] = ['Intercept', _pipe['logistic_Reg'].intercept_[0]]
        summary_table.sort_index(inplace = True)



        missing_list = get_missing_values(config.model_config.selected_names)
        df_ref_categories = pd.DataFrame(missing_list, columns = ['Feature name'])
        df_ref_categories['Coefficients'] = -1
        df_scorecard = pd.concat([summary_table, df_ref_categories], axis = 0)
        df_scorecard.reset_index(drop = True, inplace = True)
        df_scorecard['Original feature name'] = df_scorecard['Feature name'].str.split(':').str[0]

        min_sum_coef = df_scorecard.groupby('Original feature name')['Coefficients'].min().sum()
        max_sum_coef = df_scorecard.groupby('Original feature name')['Coefficients'].max().sum()

        df_scorecard['Score - Calculation'] = df_scorecard['Coefficients'] * (max_score - min_score) / (max_sum_coef - min_sum_coef)
        df_scorecard.loc[0, 'Score - Calculation'] = ((df_scorecard.loc[0,'Coefficients'] - min_sum_coef) / (max_sum_coef - min_sum_coef)) * (max_score - min_score) + min_score
        df_scorecard['Score - Preliminary'] = df_scorecard['Score - Calculation'].round()
        score_card_finaldf = df_scorecard[['Feature name', 'Score - Preliminary']]
        score_card_finaldf.columns = ['Feature', 'Score']

        acceptance_rejection = computeApprovalRejectionRate(proba_predictions, 'train', best_thresh, max_score, min_score, max_sum_coef, min_sum_coef)

        results = {
            "acceptance_rejection": acceptance_rejection,
            "score_card": score_card_finaldf,
            "version": _version,
            "errors": errors
            }

    return results

# if __name__ == '__main__':
#     scorecard()