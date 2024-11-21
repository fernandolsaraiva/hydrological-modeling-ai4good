import numpy as np
import pandas as pd


def time_delay_embedding(series: pd.Series, n_lags: int, horizon: int):
    """
    Time delay embedding
    Time series for supervised learning
    :param series: time series as pd.Series
    :param n_lags: number of past values to used as explanatory variables
    :param horizon: how many values to forecast
    :return: pd.DataFrame with reconstructed time series
    """
    assert isinstance(series, pd.Series)

    if series.name is None:
        name = 'Series'
    else:
        name = series.name

    n_lags_iter = list(range(n_lags, -horizon, -1))
    X = [series.shift(i) for i in n_lags_iter]
    X = pd.concat(X, axis=1).dropna()
    X.columns = [f'{name}(t-{j - 1})'
                 if j > 0 else f'{name}(t+{np.abs(j) + 1})'
                 for j in n_lags_iter]

    return X

def time_delay_embedding_df(df: pd.DataFrame, n_lags: int, horizon: int, station_target: str):
    """
    Apply time delay embedding to each column in the DataFrame
    :param df: input DataFrame with time series data
    :param n_lags: number of past values to use as explanatory variables
    :param horizon: how many values to forecast
    :param station_target: target station identifier
    :return: pd.DataFrame with reconstructed time series for all columns
    """
    embedded_df = pd.DataFrame()
    list_cols = []
    for column in df.columns:
        embedded_series = time_delay_embedding(df[column], n_lags, horizon)
        list_cols.append(embedded_series)
        embedded_df = pd.concat(list_cols, axis=1)
    
    # Remove all future columns except for the fluviometric variable with the specified horizon
    future_columns = [col for col in embedded_df.columns if '(t+' in col and not col.startswith(f'flu_{station_target}(t+{horizon})')]
    embedded_df = embedded_df.drop(columns=future_columns)
    
    return embedded_df