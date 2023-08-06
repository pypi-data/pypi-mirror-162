from ._base import SingleStepTransformer
from ._clippers import FeatureQuantileClipper, FeatureClipper
from ._selectors import BaseCategoricalDropper
from .utils import get_column_index
from .config import get_feature_limits, get_categorical_features
from sklearn.base import BaseEstimator, TransformerMixin

from auto_preprocess._clippers import FeatureClipper, FeatureQuantileClipper
from auto_preprocess._selectors import BaseCategoricalDropper
from auto_preprocess._function_transformers import FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    KBinsDiscretizer,
    MinMaxScaler,
    StandardScaler,
    RobustScaler,
)

from category_encoders.ordinal import OrdinalEncoder
from category_encoders.woe import WOEEncoder
from category_encoders.target_encoder import TargetEncoder
from category_encoders.sum_coding import SumEncoder
from category_encoders.m_estimate import MEstimateEncoder
from category_encoders.leave_one_out import LeaveOneOutEncoder
from category_encoders.helmert import HelmertEncoder
from category_encoders.cat_boost import CatBoostEncoder
from category_encoders.james_stein import JamesSteinEncoder
from category_encoders.one_hot import OneHotEncoder

from sklearn_pandas import DataFrameMapper


class AutoPreProcessor(BaseEstimator, TransformerMixin):

    __numeric_types = (
        "int",
        "int8",
        "int16" "int32",
        "int64",
        "float",
        "float8",
        "float16" "float32",
        "float64",
        "double",
        "numeric",
    )

    def __init__(self, features_config):

        self.features_config = features_config
        self.mapper = self.__get_pipeline_steps()

    def fit(self, X, y=None):
        self.mapper.fit(X, y)
        return self

    def transform(self, X, y=None):
        X_transf = self.mapper.transform(X)
        return X_transf

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)

    def __get_pipeline_steps(
        self,
    ):

        mapper = DataFrameMapper(
            [
                (
                    [feat_properties["name"]],
                    list(
                        filter(
                            lambda x: x is not None,
                            [
                                self.__get_imputation_transformer(feat_properties),
                                ## self.__get_categorical_dropper(feat_properties),
                                self.__get_encoders(feat_properties),
                                self.__get_clipper_transformer(feat_properties),
                                self.__get_function_transformer(feat_properties),
                                self.__get_discretizers(feat_properties),
                                self.__get_scalers(feat_properties),
                            ],
                        )
                    ),
                    {"input_df": True, "df_out": True},
                )
                for feat_properties in self.features_config
            ],
            df_out=True,
        )

        return mapper

    def __get_clipper_transformer(self, feat_properties):

        try:
            type_ = feat_properties["type"]
        except KeyError:
            type_ = None

        limits_passed = "limits" in feat_properties
        limits_is_none = (feat_properties["limits"] is None) if limits_passed else True

        qlimits_passed = "qlimits" in feat_properties
        qlimits_is_none = (
            (feat_properties["qlimits"] is None) if qlimits_passed else True
        )

        # -- testando
        if type_ in self.__numeric_types:
            if limits_is_none and not qlimits_is_none:
                clipper = FeatureQuantileClipper(
                    lower_quantile=feat_properties["qlimits"][0],
                    upper_quantile=feat_properties["qlimits"][1],
                )

            elif not limits_is_none and qlimits_is_none:
                clipper = FeatureClipper(
                    lower=feat_properties["limits"][0],
                    upper=feat_properties["limits"][1],
                )

            elif (limits_is_none) and (qlimits_is_none):
                clipper = None

            else:
                raise f"You cannot set both `qlimits` and `limits` for the feature `{feat_properties['name']}`."

        else:
            clipper = None

        return clipper

    def __get_imputation_transformer(self, feat_properties):
        imputation_strategy_passed = "imputation_strategy" in feat_properties
        imputation_fill_value_passed = "imputation_fill_value" in feat_properties

        if not imputation_strategy_passed:
            imputer = None
        else:
            imputation_strategy = feat_properties["imputation_strategy"]

            if imputation_strategy != "constant":
                imputation_fill_value = None
            else:
                imputation_fill_value = feat_properties["imputation_fill_value"]

            imputer = SimpleImputer(
                strategy=imputation_strategy, fill_value=imputation_fill_value
            )

        return imputer

    def __get_categorical_dropper(self, feat_properties):

        try:
            type_ = feat_properties["type"]
        except KeyError:
            type_ = None

        try:
            drop_categories = feat_properties["drop_categories"]
        except KeyError:
            if type_ == "categorical":
                drop_categories = []
            else:
                drop_categories = None

        if type_ != "categorical":
            dropper = None

        else:
            dropper = BaseCategoricalDropper(
                drop_categories={feat_properties["name"]: drop_categories}
            )

        return dropper

    def __get_function_transformer(self, feat_properties):

        try:
            type_ = feat_properties["type"]
        except KeyError:
            type_ = None

        try:
            transformation = feat_properties["transformation"]

        except KeyError:
            transformation = None

        if type_ not in self.__numeric_types:
            transformation = None

        if transformation is None:
            function_transformer = None

        else:
            function_transformer = FunctionTransformer(transformation=transformation)

        return function_transformer

    def __get_discretizers(self, feat_properties):

        try:
            type_ = feat_properties["type"]
        except KeyError:
            type_ = None

        try:
            discretizer_n_bins = feat_properties["discretizer_n_bins"]
        except KeyError:
            discretizer_n_bins = None

        try:
            discretizer_encode = feat_properties["discretizer_encode"]
        except KeyError:
            discretizer_encode = None

        try:
            discretizer_strategy = feat_properties["discretizer_strategy"]
        except KeyError:
            discretizer_strategy = None

        if (type_ not in self.__numeric_types) or (discretizer_n_bins is None):
            return None

        else:
            if (discretizer_n_bins is not None) and (discretizer_encode is None):
                discretizer_encode = "onehot"

            if (discretizer_n_bins is not None) and (discretizer_strategy is None):
                discretizer_strategy = "quantile"

            if (
                (discretizer_n_bins is not None)
                and (discretizer_encode is not None)
                and (discretizer_strategy is not None)
            ):

                return KBinsDiscretizer(
                    n_bins=discretizer_n_bins,
                    encode=discretizer_encode,
                    strategy=discretizer_strategy,
                )
            else:
                return None

    def __get_encoders(self, feat_properties):

        # --
        try:
            type_ = feat_properties["type"]
        except KeyError:
            type_ = None

        # --
        try:
            encode = feat_properties["encode"]
        except KeyError:
            encode = None

        # --
        try:
            discretizer_encode = feat_properties["discretizer_encode"]
        except KeyError:
            discretizer_encode = None

        # --
        if encode is None:
            return None

        else:

            if discretizer_encode is "onehot":
                return None

            else:
                if encode is None:
                    return None

                elif encode == "onehot":
                    return OneHotEncoder()

                elif encode == "woe":
                    return WOEEncoder()

                elif encode == "target":
                    return TargetEncoder()

                elif encode == "sum":
                    return SumEncoder()

                elif encode == "m_estimate":
                    return MEstimateEncoder()

                elif encode == "leave_one_out":
                    return LeaveOneOutEncoder()

                elif encode == "helmert":
                    return HelmertEncoder()

                elif encode == "cat_boost":
                    return CatBoostEncoder()

                elif encode == "james_stein":
                    return JamesSteinEncoder()

    def __get_scalers(self, feat_properties):

        # --
        try:
            type_ = feat_properties["type"]
        except KeyError:
            type_ = None

        # --
        try:
            scale = feat_properties["scale"]
        except KeyError:
            scale = None

        # --
        if scale is None:
            return None

        else:
            if scale is None:
                return None

            elif scale == "minmax":
                return MinMaxScaler()

            elif scale == "standard":
                return StandardScaler()

            elif scale == "robust":
                return RobustScaler()


class Clipper(BaseEstimator, TransformerMixin):
    def __init__(self, features_config):
        self.features_config = features_config
        self.features_to_clip = None
        self.qlimits_feature = None
        self.limits_feature = None
        self.transformers = None
        self.__transformer_class = SingleStepTransformer
        self.__transformer = None

    def fit(self, X, y=None):

        self.features_to_clip = get_feature_limits(self.features_config)

        self.qlimits_feature = {
            x[0]: x[1]["qlimits"]
            for x in filter(lambda x: "qlimits" in x[1], self.features_to_clip.items())
        }

        self.limits_feature = {
            x[0]: x[1]["limits"]
            for x in filter(lambda x: "limits" in x[1], self.features_to_clip.items())
        }

        self.transformers = [
            (
                "qlimits",
                FeatureQuantileClipper(qlimits=self.qlimits_feature),
                get_column_index(X, self.qlimits_feature.keys()),
            ),
            (
                "limits",
                FeatureClipper(limits=self.limits_feature),
                get_column_index(X, self.limits_feature.keys()),
            ),
        ]

        self.__transformer = self.__transformer_class(transformers=self.transformers)

        self.__transformer.fit(X)

        return self

    def transform(self, X, y=None):
        return self.__transformer.transform(X)

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X, y)


class CategoricalDropper(BaseEstimator, TransformerMixin):
    def __init__(self, features_config):
        self.features_config: list = features_config
        self.categorical_features: list = None
        self.categories_to_drop: dict = None
        self.__dropper_class = BaseCategoricalDropper
        self.__dropper = None

    def fit(self, X, y=None):

        self.categorical_features = get_categorical_features(self.features_config)

        self.categories_to_drop = {
            elem["name"]: elem["drop_categories"]
            for elem in filter(
                lambda x: (x["drop_categories"] is not None)
                & (x["name"] in self.categorical_features),
                self.features_config,
            )
        }

        self.__dropper = self.__dropper_class(drop_categories=self.categories_to_drop)

        self.__dropper.fit(X)

        return self

    def transform(self, X, y=None):
        return self.__dropper.transform(X)

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X, y)
