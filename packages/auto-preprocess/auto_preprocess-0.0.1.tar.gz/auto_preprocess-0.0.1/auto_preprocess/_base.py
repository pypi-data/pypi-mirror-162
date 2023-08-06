from functools import reduce
import numpy as np
from sklearn.compose import ColumnTransformer
import pandas as pd


class SingleStepTransformer(ColumnTransformer):
    """Base class for each step of automatized transformation pipeline"""

    dataframe_columns = None
    indexers = None
    transformed_columns_map = None

    def __init__(
        self,
        transformers: list,
        remainder: str = "passthrough",
        n_jobs: int = None,
        transformer_weights: dict = None,
        verbose=False,
        sparse_threshold: float = 0.3,
    ):
        self.transformers = transformers
        self.remainder = remainder
        self.n_jobs = n_jobs
        self.transformer_weights = transformer_weights
        self.verbose = verbose
        self.sparse_threshold = sparse_threshold

        super().__init__(
            transformers=self.transformers,
            remainder=self.remainder,
            n_jobs=self.n_jobs,
            transformer_weights=self.transformer_weights,
            verbose=self.verbose,
            sparse_threshold=self.sparse_threshold,
        )

    def fit(self, X: pd.DataFrame, y: pd.Series = None):

        X = self.__validate_args(X, y)

        self.dataframe_columns = X.columns

        super().fit(X)

        self.indexers = list(
            reduce(lambda x, y: x + y, [elem[2] for elem in self.transformers])
        )

        self.transformed_columns_map = {elem: i for i, elem in enumerate(self.indexers)}

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:

        X = self.__validate_args(X, y)

        X_transf = super().transform(X)

        X_final = X

        for new_index, old_index in enumerate(self.indexers):

            X = X.assign(**{X.columns[old_index]: X_transf[:, new_index]})

        return X

    def __validate_args(self, X: pd.DataFrame, y: pd.Series = None):
        """Check if input X is and dataframe or array"""

        if isinstance(X, pd.DataFrame):
            pass
        elif isinstance(X, np.ndarray):

            if self.dataframe_columns is None:
                new_columns = map(str, range(X.shape[1]))
            else:
                new_columns = self.dataframe_columns

            X = pd.DataFrame(X, columns=new_columns)
        else:
            raise ValueError("Input X must be a pandas dataframe or a numpy array.")

        return X
