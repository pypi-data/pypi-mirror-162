from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError

from multiclass_model.config.core import config


class InvoiceDataSchema(BaseModel):
    Inv_Id: Optional[int]
    Vendor_Code: Optional[int]
    GL_Code: Optional[str]
    Inv_Amt:Optional[float]
    Item_Description: Optional[str]
    


class MultipleInvoiceDataSchema(BaseModel):
    inputs: List[InvoiceDataSchema]
