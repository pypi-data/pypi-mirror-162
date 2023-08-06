import yaml
from io import StringIO

FEATURES_DEFAULT = {
    "active": True,
    "type": None,
    "limits": None,
    "qlimits": None,
    "drop_categories": None,
    "imputation_strategy": None,
    "imputation_fill_value": None,
    "discretizer_n_bins": None,
    "discretizer_encode": None,
    "discretizer_strategy": None,
    "transformation": None,
    "encode": None,
    "scale": None,
}


def get_config(filename):

    assert filename is not None, "Argument `filename` is null."

    with open(filename, "r") as file:
        features_config = yaml.safe_load(file)

    active_features = select_active_features(features_config)

    active_features = set_default_values(active_features)

    valid_features(active_features)

    return active_features


def select_active_features(features_config: dict) -> dict:

    assert features_config is not None, "Argument `filename` is null."

    active_features = list(
        filter(lambda x: x["active"] if "active" in x else True, features_config)
    )

    return active_features


def valid_features(features_config: dict) -> dict:

    assert features_config is not None, "Argument `filename` is null."

    for elem in features_config:

        # ---------------------------------
        assert (
            "name" in elem
        ), f"All features must have a `name`. Check your features config file."

        # ---------------------------------
        assert (elem["limits"] is None) | (
            elem["qlimits"] is None
        ), f"You set both `qlimits` and `limits` for the feature `{elem['name']}`. Choose one."

        # ---------------------------------
        if elem["type"] == "categorical":
            assert (elem["limits"] is None) and (
                elem["qlimits"] is None
            ), f"You cannot set or `qlimits` or `limits` for the categorical feature `{elem['name']}`."

        # ---------------------------------
        for prop in elem:
            if prop != "name":
                assert (
                    prop in FEATURES_DEFAULT
                ), f"There is no support for the feature property `{prop}` in feature `{elem['name']}`."


def set_default_values(features_config: dict) -> dict:

    assert features_config is not None, "Argument `filename` is null."

    for elem in features_config:

        for key in FEATURES_DEFAULT:
            if key not in elem:
                elem.update({key: FEATURES_DEFAULT[key]})

    return features_config


def get_feature_status(features_config):

    active_features = list(
        filter(lambda x: x["active"] if "active" in x else True, features_config)
    )

    return [elem["name"] for elem in active_features]


def get_feature_limits(features_config):

    result = {}

    for feature in features_config:

        if (feature["limits"] is None) and (feature["qlimits"] is not None):
            result.update({feature["name"]: {"qlimits": feature["qlimits"]}})

        elif (feature["qlimits"] is None) and (feature["limits"] is not None):
            result.update({feature["name"]: {"limits": feature["limits"]}})

    return result


def get_categorical_features(features_config: dict) -> list:

    categorical_features = list(
        filter(lambda x: x["type"] == "categorical", features_config)
    )

    return [elem["name"] for elem in categorical_features]


def get_features_to_drop_categories(features_config: dict) -> list:

    catfeat = get_categorical_features(features_config)

    print(catfeat)

    result = []

    for feat_properties in features_config:

        if (feat_properties["name"] in catfeat) & (
            "drop_categories" in feat_properties
        ):
            if feat_properties["drop_categories"] is not None:
                result.append(
                    {feat_properties["name"]: feat_properties["drop_categories"]}
                )

    return result


# def get_feature_names(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return [elem["name"] for elem in features_config]


# def get_feature_limits(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "limits", [None, None])
#         for params in features_config
#     }


# def get_feature_transformations(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "transformation", "identity")
#         for params in features_config
#     }


# def get_feature_types(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "type", "float")
#         for params in features_config
#     }


# def get_feature_imputation_strategy(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "imputation_strategy", "mean")
#         for params in features_config
#     }


# def get_feature_imputation_params(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "imputation_param", None)
#         for params in features_config
#     }


# def get_feature_scalers(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "scaler", None)
#         for params in features_config
#     }


# def get_feature_weights(features_config, only_actives=True):

#     if only_actives:
#         features_config = list(
#             filter(lambda x: x["active"] if "active" in x else True, features_config)
#         )

#     return {
#         params["name"]: set_default_values(params, "weight", 1)
#         for params in features_config
#     }


# def get_column_type(series):
#     dtype = series.dtype.name

#     if "int" in str(dtype):
#         dtype = "int"

#     return dtype


# def column_properties(series):

#     results = dict(
#         name=series.name,
#         active=True,
#         type=get_column_type(series),
#         limits="[left(]" + str([series.min(), series.max()]) + "[right]",
#         transformation="identity",
#         imputation_strategy="mean",
#         imputation_param=None,
#         scaler="min_max",
#         weight=1,
#     )

#     return results


# def init_config_file(dataframe, filename):

#     data = [column_properties(dataframe[col]) for col in dataframe.columns]

#     string_stream = StringIO()

#     yaml.dump(data, string_stream, default_flow_style=False, sort_keys=False)

#     main_string = string_stream.getvalue()

#     string_stream.close()

#     main_string = (
#         main_string.replace("\n- name:", "\n\n- name:")
#         .replace("'[left(]", "")
#         .replace("[right]'", "")
#     )

#     with open(filename, "w") as outfile:
#         outfile.write(main_string)
