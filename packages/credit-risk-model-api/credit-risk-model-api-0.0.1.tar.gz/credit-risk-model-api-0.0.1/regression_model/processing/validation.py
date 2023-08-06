import numpy as np
import pandas as pd
from typing import List, Optional, Tuple
from pydantic import BaseModel, ValidationError
from regression_model.config.core import config



def validate_inputs(*, input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    """Check model inputs for unprocessable values."""

    # convert syntax error field names (beginning with numbers)
    validated_data = input_data[config.model_config.features].copy() # needed
    errors = None

    try:
        # replace numpy nans so that pydantic can validate
        MultipleCreditRiskDataInputs(
            inputs=validated_data.replace({np.nan: None}).to_dict(orient="records")
        )
    except ValidationError as error:
        errors = error.json()

    return validated_data, errors


class CreditRiskInputSchema(BaseModel):
    disbursed_date: Optional[str]
    gender: Optional[str]
    age: Optional[float]
    education: Optional[str]
    marital_status: Optional[str]
    term: Optional[int]
    loan_amount: Optional[float]
    applicant_income: Optional[float]
    addr_state: Optional[str]
    annual_inc: Optional[float]
    application_type: Optional[str]
    dti: Optional[float]
    installment: Optional[float]
    apr: Optional[float]
    total_pymnt: Optional[float]
    total_rec_int: Optional[float]
    total_rec_prncp: Optional[float]
    no_of_loans: Optional[int]
    loan_type: Optional[str]
    rating: Optional[float]


class MultipleCreditRiskDataInputs(BaseModel):
    inputs: List[CreditRiskInputSchema]