import pandas as pd
import streamlit as st


def delete_nan_target_rows(df, target_variable):
    df = df.dropna(subset=[target_variable])
    return df

def remove_rows_with_nans(df: pd.DataFrame, station_target: str, n_lags: int, max_nans: int):
    columns_to_check = [f'flu_{station_target}(t-{i})' for i in range(n_lags)]
    df = df.dropna(subset=columns_to_check, thresh=len(columns_to_check) - max_nans)
    return df

def fill_missing_values_horizontal(df: pd.DataFrame, station_prefix: str, n_lags: int):
    station_columns = [col for col in df.columns if col.startswith(station_prefix)]
    for station in set(col.split('(')[0] for col in station_columns):
        cols = [f'{station}(t-{i})' for i in range(n_lags+1)]
        df[cols] = df[cols].interpolate(method='linear', axis=1, limit_direction='both')
        df[cols] = df[cols].bfill(axis=1).ffill(axis=1)
        df[cols] = df[cols].fillna(0)
    return df