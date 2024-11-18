# %%
import numpy as np
import pandas as pd

from util import (get_station_data_flu, get_station_data_plu,
                  get_station_names_plu)

# Functions
def load_pluviometric_data(start_time, end_time, station_names='all', aggregation='10-minute'):
    df = pd.DataFrame()
    
    if station_names == 'all':
        station_names = get_station_names_plu()
    
    for station_name in station_names:
        station_data = get_station_data_plu(station_name, start_time, end_time, aggregation)
        station_code = station_data['station'].iloc[0]
        station_name = 'plu_' + str(station_code)
        station_data = station_data.drop(columns=['station'])
        station_data = station_data.rename(columns={'value': station_name})
        if df.empty:
            df = station_data
        else:
            df = pd.merge(df, station_data, on='timestamp', how='outer')
    
    return df

def load_fluviometric_data(start_time, end_time, station_names=['Rio Tamanduateí - Mercado Municipal'], aggregation='10-minute'):
    df = pd.DataFrame()
    
    for station_name in station_names:
        station_data = get_station_data_flu(station_name, start_time, end_time, aggregation)
        station_code = station_data['station'].iloc[0]
        station_name = 'flu_' + str(station_code)
        station_data = station_data.drop(columns=['station'])
        station_data = station_data.rename(columns={'value': station_name})
        if df.empty:
            df = station_data
        else:
            df = pd.merge(df, station_data, on='timestamp', how='outer')
    
    return df

def load_data(start_time, end_time, station_name_flu=['Rio Tamanduateí - Mercado Municipal']):
    df_plu = load_pluviometric_data(start_time, end_time)
    df_flu = load_fluviometric_data(start_time, end_time, station_name_flu)
    
    df_combined = pd.merge(df_plu, df_flu, on='timestamp', how='outer')
    
    return df_combined

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

def time_delay_embedding_df(df: pd.DataFrame, n_lags: int, horizon: int, station_target: str = '413'):
    """
    Apply time delay embedding to each column in the DataFrame
    :param df: input DataFrame with time series data
    :param n_lags: number of past values to use as explanatory variables
    :param horizon: how many values to forecast
    :return: pd.DataFrame with reconstructed time series for all columns
    """
    embedded_df = pd.DataFrame()
    
    for column in df.columns:
        if column != 'timestamp':
            embedded_series = time_delay_embedding(df[column], n_lags, horizon)
            embedded_df = pd.concat([embedded_df, embedded_series], axis=1)
    
    # Add the timestamp column back
    embedded_df['timestamp'] = df['timestamp'].iloc[n_lags-1:len(df) - horizon].values

    # Remove all future columns except for the fluviometric variable with the specified horizon
    future_columns = [col for col in embedded_df.columns if '(t+' in col and not col.startswith(f'flu_{station_target}(t+{horizon-1})')]
    embedded_df = embedded_df.drop(columns=future_columns)
    
    return embedded_df
# %%
# Example
# Load data
start_time = '2022-01-01'
end_time = '2022-06-01'
station_name_flu = ['Rio Tamanduateí - Mercado Municipal']
load_data_bool = False
if load_data_bool == True:
    df = load_data(start_time, end_time, station_name_flu)
    df.to_csv('data/data_experimental.csv', index=False)
# %%
df = pd.read_csv('data/data_experimental.csv')
# %%
# Time Delay Embedding
n_lags = 6
horizon = 13
embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target='413')
# %%
