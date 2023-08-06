import logging
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureClipper(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        lower: float,
        upper: float,
    ):
        """Class constructor"""
        self.lower = lower
        self.upper = upper

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
        self : FeatureClipper
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
            for i in range(X.shape[1]):

                if isinstance(X, pd.DataFrame):
                    X.iloc[:, i] = np.clip(X.iloc[:, i], self.lower, self.upper)

                elif isinstance(X, np.ndarray):
                    X[:, i] = np.clip(X[:, i], self.lower, self.upper)

        except Exception as err:
            print("?????????????", X)
            logging.error(err)
            raise err

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)


class FeatureQuantileClipper(FeatureClipper):
    def __init__(
        self,
        lower_quantile: float,
        upper_quantile: float,
    ):
        """Class constructor"""
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile
        self.lower = None
        self.upper = None

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

        self.lower = np.quantile(X, self.lower_quantile)
        self.upper = np.quantile(X, self.upper_quantile)

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
            for i in range(X.shape[1]):

                if isinstance(X, pd.DataFrame):
                    X.iloc[:, i] = np.clip(X.iloc[:, i], self.lower, self.upper)

                elif isinstance(X, np.ndarray):
                    X[:, i] = np.clip(X[:, i], self.lower, self.upper)

        except Exception as err:
            logging.error(err)
            raise err

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)


# class FeatureClipper(BaseEstimator, TransformerMixin):
#     """
#     FeatureClipper.

#     Trim values at input threshold(s).

#     Assigns values outside boundary to boundary values. Thresholds
#     can be singular values or array like, and in the latter case
#     the clipping is performed element-wise in the specified axis.

#     Parameters
#     ----------
#         limits : array-like
#             An array-like value with two elementes with lower and \
#                 higher limits to be clipped.
#     """

#     def __init__(
#         self,
#         limits: dict,
#     ):
#         """Class constructor"""
#         self.limits = limits

#     def fit(self, X: pd.DataFrame, y: pd.Series = None):
#         """Fit clipper using X.

#         Parameters
#         ----------
#         X : pd.DataFrame
#             Input data of shape (n_samples, n_features).
#         y : pd.Series, optional
#             Targets for supervised learning, by default None

#         Returns
#         -------
#         self : FeatureClipper
#             This estimator.
#         """
#         return self

#     def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
#         """Applies the clip operation to the input dataframe.

#         Parameters
#         ----------
#         X : pd.DataFrame
#             Input data of shape (n_samples, n_features).
#         y : pd.Series, optional
#             Targets for supervised learning, by default None

#         Returns
#         -------
#         pd.DataFrame
#             The transformed dataframe.
#         """

#         X = X.copy()

#         try:
#             for col in self.limits:
#                 X[col] = X[col].clip(*self.limits[col])

#         except Exception as err:
#             logging.error(err)
#             raise err

#         return X

#     def fit_transform(self, X, y=None):
#         self.fit(X)
#         return self.transform(X)


# class FeatureQuantileClipper(FeatureClipper):
#     def __init__(
#         self,
#         qlimits: np.array or list or tuple,
#     ):
#         """Class constructor"""
#         self.qlimits = qlimits
#         self.limits = {}

#     def fit(self, X: pd.DataFrame, y: pd.Series = None):
#         """Fit clipper using X.

#         Parameters
#         ----------
#         X : pd.DataFrame
#             Input data of shape (n_samples, n_features).
#         y : pd.Series, optional
#             Targets for supervised learning, by default None

#         Returns
#         -------
#         self : FeatureQuantileClipper
#             This estimator.
#         """

#         for col in self.qlimits:
#             self.limits[col] = X[col].quantile(self.qlimits[col]).to_list()

#         return self

#     def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
#         """Applies the clip operation to the input dataframe.

#         Parameters
#         ----------
#         X : pd.DataFrame
#             Input data of shape (n_samples, n_features).
#         y : pd.Series, optional
#             Targets for supervised learning, by default None

#         Returns
#         -------
#         pd.DataFrame
#             The transformed dataframe.
#         """

#         X = X.copy()

#         try:
#             for col in self.limits:
#                 X[col] = X[col].clip(*self.limits[col])

#         except Exception as err:
#             logging.error(err)
#             raise err

#         return X

#     def fit_transform(self, X, y=None):
#         self.fit(X)
#         return self.transform(X)
