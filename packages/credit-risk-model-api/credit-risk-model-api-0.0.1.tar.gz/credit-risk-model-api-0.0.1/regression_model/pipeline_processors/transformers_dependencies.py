import pandas as pd
import numpy as np
from typing import List
from sklearn.base import BaseEstimator, TransformerMixin


def remove_empty_spaces(data):
    data = data.replace(' ', '', regex=True)
    return data

def strPreprocessing(data):
    data = data.str.replace("\s","", regex=True).str.lower()
    return data

def multipleReplace(df, list_item, value):
    list_item = [x.lower() for x in list_item]
    value = value*len(list_item)
    required_dict = dict(zip(list_item, value))
    df = df.replace(required_dict)
    return df


def multipleReplaceNaNs(df, list_item, value):
    value = value*len(list_item)
    required_dict = dict(zip(list_item, value))
    df = df.replace(required_dict)
    return df

def str_rating_preprocessing(data):
    data = data.replace("\+","", regex=True)
    data = data.replace("\-","", regex=True)
    data = data.astype(float)
    return data

def data_cleansing(df):
    dff = df.copy()
    # get a list of columns that have more than 80% null values
    na_values = dff.isnull().mean()
    na_values[na_values>0.8]
    # drop columns with more than 80% null values
    dff.dropna(thresh = dff.shape[0]*0.2, how = 'all', axis = 1, inplace = True)
    '''
    drop redundant and forward-looking columns
    '''
    drop_fields_list = ['id', 'employer_name', 'Residential Address', 'loan_amnt', 'term']
    dff.drop(columns = drop_fields_list, axis = 1, inplace = True)
    """
    # Rename columns and convert them to lowercase.
    # """
    rename_dict = {'issue_d':'disbursed_date',
                   'Total Loan as a function of annual income': 'loan_amount',
                   'int_rate':'apr',
                   'Tenor': 'term'}
    dff = dff.rename(columns = rename_dict)
    dff.columns = [x.lower().replace(' ', '_') for x in dff.columns]
    for col in dff.columns:
        if list(dff[col].unique()) == [' ']:
            dff.drop(columns = [col], axis = 1, inplace = True)
    dff = remove_empty_spaces(dff)
    dff['rating'] = str_rating_preprocessing(dff['rating'])
    object_columns = list(dff.select_dtypes(include = 'object').copy().columns)
    dff[object_columns] = dff[object_columns]
    dff[object_columns] = dff[object_columns].apply(lambda x: x.astype(str).str.lower())
    dff = dff[(dff['application_type']!= 'part-liquidation') & (dff['application_type']!= 'restructured')].reset_index(drop = True)
    return dff

def targetVariablePreprocess(X):
    dff = X.copy()
    dff = dff[(dff['loan_status'] != 'running')]
    dff['disbursed_date'] = pd.to_datetime(dff['disbursed_date'])
    dff['last_pymnt_d'] = pd.to_datetime(dff['last_pymnt_d'])
#     print(dff['last_pymnt_d'])
    dff['real_months_tenor'] = pd.to_numeric((dff['last_pymnt_d'] - dff['disbursed_date']) / np.timedelta64(1, 'M'))
    dff['teno_diff_days'] = round((dff['real_months_tenor'] - dff['term'].astype(int)) * 31)
    dff['deficit'] = dff['loan_amount'] - dff['total_pymnt']
    # Drop columns as they are now useless
    dff.drop(columns = ['last_pymnt_d', 'last_pymnt_amnt'], inplace = True)

    col1 = 'teno_diff_days'
    col2 = 'deficit'
    col3 = "loan_status"

    cond1 = ((dff[col1] > 90) & (dff[col2] > 0) | (dff[col3] == 'Written Off'))
    cond2 = ((dff[col1] > 90) & (dff[col2] == 0))
    cond3 = ((dff[col1] > 30) & ((dff[col1] <= 90) | (dff[col3] == '90') | (dff[col3] == '83')) & (dff[col2] == 0))
    cond4 = ((dff[col1] > 2) & ((dff[col1] <= 30) | (dff[col3] == '30')) & (dff[col2] == 0))

    dff["final_status"] = np.where(cond1, 'Charged off',
                                 (np.where(cond2, 'Does not meet the credit policy. Status: Fully paid',
                                           np.where(cond3, 'Late (31-90 days)',
                                                   np.where(cond4, 'Late (2-30 days)',
                                                           'Fully Paid'))))
                                 )
    dff.drop(['real_months_tenor', 'teno_diff_days', 'deficit'], axis = 1, inplace = True)
    return dff

def convertTargetToBinary(X):
    dff = X.copy()
    colDelete = ['Charged off',
                 'Does not meet the credit policy. Status: Fully paid',
                 'Late (31-90 days)',
                 'Late (2-30 days)']
    # create a new column based on the final_status column that will be our target variable
    dff['final_status'] = np.where(dff.loc[:, 'final_status'].isin(colDelete), 0, 1)
    # Drop the original 'loan_status' column
    dff.drop(columns = ['loan_status'], inplace = True)
    return dff

def preprocess(X):
    dff = X.copy()
    dff['dti'] = round((dff['installment']/dff['applicant_income']) * 100, 2)

    # rating
    dff['rating'] = dff['rating'].astype(float)

    variables_to_be_categorized = ['age', 'loan_amount', 'no_of_loans', 'applicant_income', 'dti', 'term', 'rating']
    needed_columns = list(set(list(dff.columns)) - set(variables_to_be_categorized))
    dff[needed_columns] = multipleReplaceNaNs(dff[needed_columns], [np.inf, -np.inf, np.nan, float('nan'), 'none', 'nan', ''], ['missing'])
    dff[needed_columns] = dff[needed_columns].fillna('missing')

    # education
    dff['education'] = multipleReplace(dff['education'],
                                           ["postgraduate","postgrad"],
                                           ['postgraduate'])
    dff['education'] = multipleReplace(dff['education'],
                                           ["secondaryschool","secondary", 'ssce'],
                                           ['secondary'])
    dff['education'] = multipleReplace(dff['education'],
                                           ['graduate', 'university', 'b.sc', 'bsc'],
                                           ['tertiary'])

    # marital_status
    dff['marital_status'] = multipleReplace(dff['marital_status'],
                                           ['Separated/Divorced', 'Separated', 'SEPERATED'],
                                           ['divorced'])
    dff['marital_status'] = multipleReplace(dff['marital_status'],
                                           ['Widowed', 'Widow', 'Widower'],
                                           ['widow_widower'])
    dff['marital_status'] = multipleReplace(dff['marital_status'],
                                           ['Other', 'OTHERS', 'TERTIARY'],
                                           ['missing'])

    # gender
    dff['gender'] = multipleReplace(dff['gender'],
                                     ['Male', 'MALE', 'male',],
                                     ['male'])
    dff['gender'] = multipleReplace(dff['gender'],
                                     ['Female', 'FEMALE', 'female', 'FEMALE ', 'FEMale' ],
                                     ['female'])

    # addr_state
    dff['addr_state'] = multipleReplace(dff['addr_state'],
                                        ['lagosstate'],
                                        ['lagos'])
    dff['addr_state'] = multipleReplace(dff['addr_state'],
                                     ['Oyostate'],
                                     ['oyo'])
    dff['addr_state'] = multipleReplace(dff['addr_state'],
                                     ['kanostate'],
                                     ['kano'])

    dff['application_type'] = multipleReplace(dff['application_type'],
                                                ['new', 'newloan'],
                                                ['newloan'])

    dff = dff.drop(['total_pymnt',
                    'total_rec_int',
                     # 'total_rec_prncp', # delete these, as they are not required at the moment of loan request
                    'loan_type',
                    'addr_state'], axis = 1) # loan_type and addr_state should be deleted as it contains old and new inf

    return dff

def preprocessNumericVariables(X):
    # explore the unique values in loan_status column
    dff = X.copy()

    # age_interval
    cutlist = [0, 22, 27, 32, 37, 42, 47, 52, 57, 62, 120]
    dff['age_interval'] = pd.cut(dff.age, cutlist).values.add_categories('missing')
    dff['age_interval'] = dff['age_interval'].fillna('missing')

    # loan_amount_interval
    amtcutlist = [0, 5e5, 1e6, 1.5e6, 2e6, 2.5e6, 3e6, 3.5e6, 4e6, 4.5e6, 5e6, 5.5e6, 6e6, 1e12]
    dff['loan_amount_interval'] = pd.cut(dff.loan_amount, amtcutlist).values.add_categories('missing')
    dff['loan_amount_interval'] = dff['loan_amount_interval'].fillna('missing')

    no_of_loans_cutlist = list(range(0, 50, 4))
    dff['no_of_loans_interval'] = pd.cut(dff.no_of_loans, no_of_loans_cutlist).values.add_categories('missing')
    dff['no_of_loans_interval'] = dff['no_of_loans_interval'].fillna('missing')

    # applicant_monthly_income_interval
    mth_income_cutlist = list(range(0, 3_100_000, 100000)) + [1e9]
    dff['monthly_income_interval'] = pd.cut(dff.applicant_income, mth_income_cutlist).values.add_categories('missing')
    dff['monthly_income_interval'] = dff['monthly_income_interval'].fillna('missing')

    # dti_interval
    dti_cutlist = [0, 10, 20, 30, 40, 50, 60, 100000]
    dff['dti_interval'] = pd.cut(dff.dti, dti_cutlist).values.add_categories('missing')
    dff['dti_interval'] = dff['dti_interval'].fillna('missing')

    # tenor_interval
    term_cutlist = list(range(0, 19)) + [1000]
    dff['term_interval'] = pd.cut(dff.term, term_cutlist).values.add_categories('missing')
    dff['term_interval'] = dff['term_interval'].fillna('missing')

    # rating_interval
    rating_cutlist = list(range(0, 21)) + [1000]
    dff['rating_interval'] = pd.cut(dff.rating, rating_cutlist).values.add_categories('missing')
    dff['rating_interval'] = dff['rating_interval'].fillna('missing')
    return dff


class DataCleansing(BaseEstimator, TransformerMixin):
    def __init__(self, variables = None): # no *args or *kargs
        self.variables = variables

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    # function to create dummy variables
    def transform(self, X):
        # print(X)
        dff = data_cleansing(X.copy())
        return dff

class TargetVariablePreprocess(BaseEstimator, TransformerMixin):
    def __init__(self, variables = None): # no *args or *kargs
        self.variables = variables

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    # function to create dummy variables
    def transform(self, X):
        dff = targetVariablePreprocess(X.copy())
        return dff

class Preprocess(BaseEstimator, TransformerMixin):
    def __init__(self, variables = None): # no *args or *kargs
        self.variables = variables

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    # function to create dummy variables
    def transform(self, X):
        dff = preprocess(X.copy())
        return dff

class PreprocessNumericVariables(BaseEstimator, TransformerMixin):
    def __init__(self, variables = None): # no *args or *kargs
        self.variables = variables

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    # function to create dummy variables
    def transform(self, X):
        dff = preprocessNumericVariables(X.copy())
        return dff

class ConvertTargetToBinary(BaseEstimator, TransformerMixin):
    def __init__(self, variables = None): # no *args or *kargs
        self.variables = variables

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    # function to create dummy variables
    def transform(self, X):
        dff = convertTargetToBinary(X.copy())
        return dff

class DummyTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, columns_list: List[str]): # no *args or *kargs
        if not isinstance(columns_list, list):
            raise ValueError('columns_list should be a list.')
        self.columns_list = columns_list

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    def get_missing_values(self, df: pd.DataFrame):
        missing_list = []
        for item in df.columns:
            if ('missing') in item  or ('Missing') in item:
                missing_list.append(item)
        return missing_list

    # function to create dummy variables
    def transform(self, X):
        X_ = X.copy()
        df_dummies = []
        for col in self.columns_list:
            try:
                df_dummies_single = pd.get_dummies(X_[col], prefix = col, prefix_sep = ':')
                df_dummies.append(df_dummies_single)
            except Exception as e:
                print(e)

        df_dummies = pd.concat(df_dummies, axis = 1)
        missing_list = self.get_missing_values(df_dummies)
        df_dummies.drop(missing_list, axis=1, inplace = True)
        return df_dummies

def targetVariablePreprocessRunningLoans(X):
    dff = X.copy()
#     print(X)
    dff = dff[(dff['loan_status'] == 'running')]
    return dff



class TargetVariablePreprocessRunningLoans(BaseEstimator, TransformerMixin):
    def __init__(self, variables = None): # no *args or *kargs
        self.variables = variables

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        return self # nothing else to do

    # function to create dummy variables
    def transform(self, X):
        dff = targetVariablePreprocess(X.copy())
        return dff