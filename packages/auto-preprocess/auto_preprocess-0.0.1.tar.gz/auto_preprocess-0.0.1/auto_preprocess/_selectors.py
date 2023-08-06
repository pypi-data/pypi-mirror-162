import logging
import numpy as np
import pandas as pd
from typing import Any
from sklearn.base import BaseEstimator, TransformerMixin


class BaseCategoricalSelector(BaseEstimator, TransformerMixin):
    """
    CategoriesSelector.

    Keep only the categories informed by the user. Undesired
    categories will be conveted to NaN.

    Parameters
    ----------
        categories : array-like
            An array-like value with two elementes with lower and \
                higher limits to be clipped.
    """

    def __init__(
        self,
        categories: dict,
        default_value: Any = np.nan,
    ):
        """Class constructor"""
        self.categories: dict = categories
        self.default_value: Any = default_value

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit clipper using X.

        Parameters
        ----------
        X : pd.DataFrame
            Input data of shape (n_samples, n_features).
        y : pd.Series, optional
            Targets for supervised learning, by default None

        Returns
        -------
        self : FeatureQuantileClipper
            This estimator.
        """

        return self

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """Applies the clip operation to the input dataframe.

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

        X = X.copy()

        try:
            for col in self.categories:
                X = X.assign(
                    **{
                        col: np.where(
                            X[col].isin(self.categories[col]),
                            X[col],
                            self.default_value,
                        )
                    }
                )

        except Exception as err:
            logging.error(err)
            raise err

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)


class BaseCategoricalDropper(BaseEstimator, TransformerMixin):
    """
    BaseCategoricalDropper.

    Convet all the categories informed by the user for each column,\
    to NaN.

    Parameters
    ----------
        drop_categories: dict
            A dict parameter where the keys are the column \
                names and the values ara lists with the categories\
                to be dropped

        default_value: any
            The value to replace the categories to be dropped.
    """

    def __init__(
        self,
        drop_categories: dict,
        default_value: Any = np.nan,
    ):
        """Class constructor"""
        self.drop_categories: dict = drop_categories
        self.default_value: Any = default_value
        self.columns = None

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit clipper using X.

        Parameters
        ----------
        X : pd.DataFrame
            Input data of shape (n_samples, n_features).
        y : pd.Series, optional
            Targets for supervised learning, by default None

        Returns
        -------
        self : FeatureQuantileClipper
            This estimator.
        """

        self.columns = X.columns

        return self

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """Applies the clip operation to the input dataframe.

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

        X = X.copy()

        try:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X)

            for col in self.drop_categories:
                X = X.assign(
                    **{
                        col: np.where(
                            X[col].isin(self.drop_categories[col]),
                            self.default_value,
                            X[col],
                        )
                    }
                )

        except Exception as err:
            logging.error(err)
            raise err

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)
