import logging
import numpy as np
import pandas as pd
from typing import Any
from sklearn.base import BaseEstimator, TransformerMixin


class FunctionTransformer(BaseEstimator, TransformerMixin):
    """
    FeatureTransformer.
    
    Applies a transformation dataframe.

    Parameters
    ----------
        transformation : {'log', 'log10', 'exp', 'square',\
            'sqrt', 'identity'}, default='identity'
            A string with the decription of a transformation to be applied.
    """

    def __init__(self, transformation: str = "identity"):
        """Class constructor"""
        self.transformation = transformation
        self.transformer = self.__interpret_transformation(self.transformation)

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit transformations using X.

        Parameters
        ----------
        X : pd.DataFrame
            Input data of shape (n_samples, n_features).
        y : pd.Series, optional
            Targets for supervised learning, by default None

        Returns
        -------
        self : FeatureTransformer
            This estimator.
        """
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """Applies the transformation to the input dataframe.

        Parameters
        ----------
        X : pd.DataFrame
            Input data of shape (n_samples, n_features).
        y : pd.Series, optional
            Targets for supervised learning, by default None

        Returns
        -------
        pd.DataFrame
            The transformed dataframe.
        """

        try:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X)

            X = X.apply(self.transformer)

        except Exception as err:
            logging.error(err)
            raise err

        return X

    def fit_transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """Fit transformations using X and return the transformed dataframe.

        Parameters
        ----------
        X : pd.DataFrame
            Input data of shape (n_samples, n_features).
        y : pd.Series, optional
            Targets for supervised learning, by default None

        Returns
        -------
        pd.DataFrame
            The transformed dataframe.
        """

        self.fit(X)

        return self.transform(X)

    def __interpret_transformation(self, transformation: str = "identity"):
        """Returns a function related to the transformation operation.

        Parameters
        ----------
        transformation : {'log', 'log10', 'exp', 'square',\
            'sqrt', 'identity'}, default='identity'
            A string with the decription of a transformation to be applied.

        Returns
        -------
        function
            A function related to the transformation operation.
        """

        if transformation == "log":
            return np.log

        elif transformation == "log10":
            return np.log10

        elif transformation == "log1p":
            return np.log1p

        elif transformation == "exp":
            return np.exp

        elif transformation == "square":
            return np.square

        elif transformation == "sqrt":
            return np.sqrt

        elif transformation == "identity":
            return lambda x: x

        else:
            raise ValueError(
                f"The value {transformation} for 'transformation' is not supported."
            )
