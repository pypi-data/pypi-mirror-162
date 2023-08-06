import yaml
from io import StringIO

EXAMPLE_HEADER = """\
###################################################
# FEATURES - CONFIGURATION EXAMPLE
#
# >>> Example:
# - name: nome_da_feature
#   active: true
#   type: float
#   imputation_strategy: constant # (constant, mean, median)
#   imputation_fill_value: 1 # only applicable to constant strategy
#   limits: [0.0, 1705.0] # if set limits, do not set qlimits
#   qlimits: [0,0.95] # quantile limts; if set qlimits, do not set limits
#   transformation: identity # (log, log10, log1p, exp, square, sqrt, identity)
#   discretizer_n_bins: null
#   discretizer_encode: "ordinal" # (ordinal, onehot)
#   discretizer_strategy: quantile # (uniform, quantile, kmeans)
#   encoder: m_estimate # (onehot, woe, target, sum, m_estimate, leave_one_out, helmert, cat_boost, james_stein)
#   scaler: minmax #(minmax, standard, robust)

"""


def generate_features_config_example(df, filepath):

    obj = [
        {
            "name": col,
            "type": "float",
            "active": True,
            "encode": None,
            "imputation_strategy": "median",
            "imputation_fill_value": 0,
            "qlimits": [0, 1],
            "limits": None,
            "transformation": "identity",
            "discretizer_n_bins": None,
            "discretizer_encode": "ordinal",
            "discretizer_strategy": "quantile",
            "scale": "minmax",
        }
        for col in df
    ]

    output = StringIO()

    yaml.dump(obj, output, sort_keys=False)

    text = EXAMPLE_HEADER + output.getvalue().replace("\n- ", "\n\n- ")

    with open(filepath, "w") as file:
        file.write(text)
