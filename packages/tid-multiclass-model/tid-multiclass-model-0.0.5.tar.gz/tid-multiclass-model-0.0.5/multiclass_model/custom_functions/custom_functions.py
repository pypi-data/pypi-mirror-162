from typing import List

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class splitter(BaseEstimator, TransformerMixin):
    
    def __init__(self, variables: List[str], new_variable_names: List[str]):
        
        if not isinstance(variables, list):
            raise ValueError('variables should be a list')
            
        self.variables = variables
        self.new_variable_names = new_variable_names
        
    def fit(self, X: pd.DataFrame, y:pd.Series = None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X) -> pd.DataFrame:
        X = X.copy()
        for feature, feature_name in zip(self.variables, self.new_variable_names):
            X[[feature, feature_name]] = X[feature].str.split('-',expand=True)

        return X


class Mapper(BaseEstimator, TransformerMixin):
    """Categorical variable mapper."""

    def __init__(self, variables: List[str], mappings: dict):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.mappings = mappings

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].map(self.mappings)

        return X
    
class Custom_Fillna(BaseEstimator, TransformerMixin):
    
    def __init__(self, variables: List[str], fill_value: int):
        
        if not isinstance(variables, list):
            raise ValueError('variables should be a list')
            
        self.variables = variables
        self.fill_value = fill_value
        
    def fit(self, X : pd.DataFrame, y: pd.Series = None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X: pd.DataFrame):
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].fillna(self.fill_value)

        return X