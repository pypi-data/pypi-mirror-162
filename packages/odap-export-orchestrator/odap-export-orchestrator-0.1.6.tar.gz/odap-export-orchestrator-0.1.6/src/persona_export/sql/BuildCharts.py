from pydantic import BaseModel
import re
from typing import Any
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.ensemble import RandomForestClassifier


class WrongInputHanlder(Exception):
    """Exception for """

class Query(BaseModel):
    '''Basic query schema'''
    query: str


def build_charts(
        query_string: Query,
        df_ref: pd.DataFrame,
) -> Any:
    """Calculate chars inside"""
    output = {"total": None, "options": []}
    metric = ["mean", "median", "t_value1", "t_value2", "ks", "rf"][0]

    if query_string.query:
        try:
            df_selected = df_ref.query(query_string.query)
        except pd.core.computation.ops.UndefinedVariableError:
            raise WrongInputHanlder()
        stats_query = df_selected.describe().rename(index={"50%": "median"})
        if "t_value" in metric:
            stats_full = df_ref.describe()
            stats_query.loc["t_value1"] = (
                                                  stats_query.loc["mean"] - stats_full.loc["mean"]
                                          ) / (stats_query.loc["std"] / np.sqrt(stats_query.loc["count"]))
            stats_query.loc["t_value2"] = (
                                                  stats_query.loc["mean"] - stats_full.loc["mean"]
                                          ) / np.sqrt(
                (stats_query.loc["std"] / np.sqrt(stats_query.loc["count"])) ** 2
                + (stats_full.loc["std"] / np.sqrt(stats_full.loc["count"])) ** 2
            )
        elif metric == "ks":
            stats_query.loc["ks"] = df_selected[stats_query.columns].apply(
                lambda x: 1 - ks_2samp(x.dropna(), df_ref[x.name].dropna())[0]
            )
        elif metric == "rf":
            df_selected["label"] = 1
            df_model = df_ref.merge(
                df_selected.label, how="left", left_index=True, right_index=True
            ).fillna(0)
            cols_drop = set(re.split("=|<|>| ", query_string.query)).intersection(
                output.keys()
            )
            X = df_model[stats_query.columns].drop(list(cols_drop), 1)
            y = df_model["label"]

            rf = RandomForestClassifier(max_depth=5, n_estimators=20)
            rf.fit(X, y)

            feat_dict = {
                name: value for name, value in zip(X.columns, rf.feature_importances_)
            }
            for col in cols_drop:
                feat_dict[col] = 0
            stats_query = stats_query.append(pd.Series(feat_dict, name="rf"))
        stats_query.replace([np.inf, -np.inf], 0, inplace=True)
    else:
        df_selected = df_ref._get_numeric_data()
        if metric in ["mean", "median"]:
            # stats_query = df_selected.describe().rename(index={'50%': 'median'})
            stats_query = pd.concat(
                [
                    df_selected.mean().rename("mean"),
                    df_selected.count().rename("count"),
                ],
                axis=1,
            ).T
        else:
            stats_query = pd.DataFrame(
                [], columns=df_selected.columns, index=[metric, "count"]
            )
            stats_query.loc["count"] = df_selected.count()
            stats_query.loc[metric] = 1
    output["total"] = df_selected.shape[0]
    stats_query = stats_query.fillna(0)
    for i in stats_query.columns:
        if i != "client_id":
            output["options"].append(
                {
                    "id": i,
                    "value": round(stats_query.loc[metric, i], 2),
                    "count": int(stats_query.loc["count", i]),
                }
            )
    df = df_ref.loc[:, df_ref.dtypes == object]
    for i in df_ref.select_dtypes(include=[object]):
        if i != "client_id" and "date" not in i:
            values = df[i].value_counts()
            for rname in values.keys():
                output["options"].append(
                    {"id": rname, "value": 0, "count": int(values[rname])}
                )
    return output
