# %%
import os
import sys
import streamlit as st

# Adiciona o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import pandas as pd

from util import (get_station_code_flu, get_station_data_flu, get_station_data_plu,
                  get_station_names_plu, get_multiple_station_data_plu)


# %%
# def load_pluviometric_data(start_time, end_time, station_names='all', aggregation='10-minute'):
#     df = pd.DataFrame()
#     if station_names == 'all':
#         station_names = get_station_names_plu()
#     for station_name in station_names:
#         station_data = get_station_data_plu(station_name, start_time, end_time, aggregation)
#         station_code = get_station_code_plu(station_name)
#         station_name = 'plu_' + str(station_code)
#         station_data = station_data.drop(columns=['station'])
#         station_data = station_data.rename(columns={'value': station_name})
#         if df.empty:
#             df = station_data
#         else:
#             df = pd.merge(df, station_data, on='timestamp', how='outer')
#     return df

def load_pluviometric_data(start_time, end_time, station_names='all', aggregation='10-minute'):
    df = pd.DataFrame()
    if station_names == 'all':
        station_names = get_station_names_plu()
    df = get_multiple_station_data_plu(station_names, start_time, end_time, aggregation)
    return df

def load_fluviometric_data(start_time, end_time, station_names=['Rio Tamanduateí - Mercado Municipal'], aggregation='10-minute'):
    df = pd.DataFrame()
    for station_name in station_names:
        station_data = get_station_data_flu(station_name, start_time, end_time, aggregation)
        station_code = get_station_code_flu(station_name)
        station_name = 'flu_' + str(station_code)
        station_data = station_data.drop(columns=['station'])
        station_data = station_data.rename(columns={'value': station_name})
        if df.empty:
            df = station_data
        else:
            df = pd.merge(df, station_data, on='timestamp', how='outer')
    return df

# def ensure_timestamp(df):
#     df.columns = df.columns.str.lower()

#     # Caso ideal
#     if 'timestamp' in df.columns:
#         return df

#     # Se virou índice
#     if df.index.name == 'timestamp':
#         return df.reset_index()

#     # Casos comuns de reset_index duplicado
#     if 'index' in df.columns:
#         return df.rename(columns={'index': 'timestamp'})
    
#     if 'level_0' in df.columns:
#         return df.rename(columns={'level_0': 'timestamp'})

#     # Último fallback
#     raise ValueError(f"Timestamp não encontrado nas colunas: {df.columns}")

def ensure_timestamp(df):
    df.columns = df.columns.str.lower()

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        return df

    if df.index.name == 'timestamp':
        df = df.reset_index()
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        return df

    if 'index' in df.columns:
        df = df.rename(columns={'index': 'timestamp'})
    elif 'level_0' in df.columns:
        df = df.rename(columns={'level_0': 'timestamp'})
    else:
        raise ValueError(f"Timestamp não encontrado: {df.columns}")

    # ⚠️ aqui é crucial
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    return df

def load_data(start_time, end_time, station_name_flu=['Rio Tamanduateí - Mercado Municipal']):
    df_plu = load_pluviometric_data(start_time, end_time)
    df_flu = load_fluviometric_data(start_time, end_time, station_name_flu)
    
    df_plu.columns = df_plu.columns.str.lower()
    df_flu.columns = df_flu.columns.str.lower()

    df_plu = ensure_timestamp(df_plu)
    df_flu = ensure_timestamp(df_flu)

    # print("BEFORE MERGE")
    # print("df_plu columns:", df_plu.columns)
    # print("df_plu index:", df_plu.index.names)
    # print("df_flu columns:", df_flu.columns)
    # print("df_flu index:", df_flu.index.names)

    df_plu['timestamp'] = pd.to_datetime(df_plu['timestamp'], errors='coerce')

    if df_plu['timestamp'].dt.tz is None:
        df_plu['timestamp'] = df_plu['timestamp'].dt.tz_localize('UTC')

    df_plu['timestamp'] = df_plu['timestamp'].dt.tz_convert('America/Sao_Paulo')


    df_flu['timestamp'] = pd.to_datetime(df_flu['timestamp'], errors='coerce')

    if df_flu['timestamp'].dt.tz is None:
        df_flu['timestamp'] = df_flu['timestamp'].dt.tz_localize('UTC')

    df_flu['timestamp'] = df_flu['timestamp'].dt.tz_convert('America/Sao_Paulo')

    # print(df_plu['timestamp'].dt.tz)
    # print(df_flu['timestamp'].dt.tz)

    df_combined = pd.merge(df_plu, df_flu, on='timestamp', how='outer')
    return df_combined