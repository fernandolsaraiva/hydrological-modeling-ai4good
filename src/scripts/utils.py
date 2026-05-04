# %%
import os
import sys
import streamlit as st

# Adiciona o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import pandas as pd

from util import (get_station_code_flu, get_station_data_flu, get_station_data_plu,
                  get_station_names_plu, get_multiple_station_data_plu)

def load_pluviometric_data(start_time, end_time, station_names='all', aggregation='10-minute'):
    df = pd.DataFrame()
    if station_names == 'all':
        station_names = get_station_names_plu()
    df = get_multiple_station_data_plu(station_names, start_time, end_time, aggregation)
    return df

def load_fluviometric_data(start_time, end_time, station_names=['Rio Tamanduateí - Mercado Municipal'], aggregation='10-minute'):
    df = pd.DataFrame()
    
    for station_name in station_names:
        print(f"\n➡️ Buscando estação: {station_name}")
        
        station_data = get_station_data_flu(station_name, start_time, end_time, aggregation)
        
        if station_data.empty:
            print("⚠️ ESTAÇÃO SEM DADOS")
            continue  # importante pra não quebrar depois
        
        station_code = get_station_code_flu(station_name)
        new_col_name = 'flu_' + str(station_code)
        
        station_data = station_data.drop(columns=['station'], errors='ignore')
        station_data = station_data.rename(columns={'value': new_col_name})
        
        if df.empty:
            df = station_data
        else:
            df = pd.merge(df, station_data, on='timestamp', how='outer')

        # 🔥 FIX CRÍTICO
        if df.empty:
            return pd.DataFrame(columns=['timestamp'])
    return df

def ensure_timestamp(df):
    if df is None or df.empty:
        return df

    if not isinstance(df.columns, pd.Index):
        return df

    df.columns = df.columns.astype(str).str.lower()

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        return df

    if hasattr(df.index, "name") and df.index.name == 'timestamp':
        df = df.reset_index()
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        return df

    if 'index' in df.columns:
        df = df.rename(columns={'index': 'timestamp'})
    elif 'level_0' in df.columns:
        df = df.rename(columns={'level_0': 'timestamp'})
    else:
        raise ValueError(f"Timestamp não encontrado: {list(df.columns)}")

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    return df

def safe_lower_columns(df):
    if df is None or df.empty:
        return df

    if not isinstance(df.columns, pd.Index):
        return df

    df.columns = df.columns.astype(str).str.lower()
    return df

def load_data(start_time, end_time, station_name_flu=['Rio Tamanduateí - Mercado Municipal']):
    df_plu = load_pluviometric_data(start_time, end_time)
    df_flu = load_fluviometric_data(start_time, end_time, station_name_flu)

    # ----------------------------
    # 1. Tratamento seguro de vazios
    # ----------------------------
    if df_plu is None or df_plu.empty:
        return pd.DataFrame()

    if df_flu is None or df_flu.empty:
        print("⚠️ df_flu vazio - retornando apenas pluviométrico")
        df_flu = pd.DataFrame(columns=["timestamp"])

    # ----------------------------
    # 2. Normalização de colunas (segura)
    # ----------------------------
    def safe_lower(df):
        if df is not None and isinstance(df.columns, pd.Index):
            df.columns = df.columns.astype(str).str.lower()
        return df

    df_plu = safe_lower(df_plu)
    df_flu = safe_lower(df_flu)

    # ----------------------------
    # 3. Garantir timestamp no PLU
    # ----------------------------
    df_plu = ensure_timestamp(df_plu)

    df_plu["timestamp"] = pd.to_datetime(df_plu["timestamp"], errors="coerce")

    if df_plu["timestamp"].dt.tz is None:
        df_plu["timestamp"] = df_plu["timestamp"].dt.tz_localize("UTC")

    df_plu["timestamp"] = df_plu["timestamp"].dt.tz_convert("America/Sao_Paulo")

    # ----------------------------
    # 4. Garantir timestamp no FLU (se existir dado)
    # ----------------------------
    if "timestamp" in df_flu.columns and not df_flu.empty:

        df_flu["timestamp"] = pd.to_datetime(df_flu["timestamp"], errors="coerce")

        if df_flu["timestamp"].dt.tz is None:
            df_flu["timestamp"] = df_flu["timestamp"].dt.tz_localize("UTC")

        df_flu["timestamp"] = df_flu["timestamp"].dt.tz_convert("America/Sao_Paulo")

    else:
        # garante coluna para merge não quebrar
        df_flu = pd.DataFrame(columns=["timestamp"])

    # ----------------------------
    # 5. Garantir timestamp final antes do merge
    # ----------------------------
    if "timestamp" not in df_plu.columns:
        df_plu = df_plu.reset_index()

    if "timestamp" not in df_flu.columns:
        df_flu = df_flu.reset_index()

    # ----------------------------
    # 6. Merge seguro
    # ----------------------------
    df_combined = pd.merge(df_plu, df_flu, on="timestamp", how="outer")

    return df_combined

# def load_data(start_time, end_time, station_name_flu=['Rio Tamanduateí - Mercado Municipal']):
#     df_plu = load_pluviometric_data(start_time, end_time)
#     df_flu = load_fluviometric_data(start_time, end_time, station_name_flu)
#     # print("FLU timestamps:", df_flu['timestamp'].head()) 
#     if df_flu is not None and not df_flu.empty and 'timestamp' in df_flu.columns:
#         print("FLU timestamps:", df_flu['timestamp'].head())
#     else:
#         print("⚠️ FLU vazio ou sem timestamp")

#     df_flu = safe_lower_columns(df_flu)
#     df_plu = safe_lower_columns(df_plu)

#     # df_plu.columns = df_plu.columns.str.lower()
#     # # df_flu.columns = df_flu.columns.str.lower()
#     # if not df_flu.empty and isinstance(df_flu.columns, pd.Index):
#     #     df_flu.columns = df_flu.columns.str.lower()

#     df_plu = ensure_timestamp(df_plu)
#     df_flu = ensure_timestamp(df_flu)

#     df_plu['timestamp'] = pd.to_datetime(df_plu['timestamp'], errors='coerce')

#     if df_plu['timestamp'].dt.tz is None:
#         df_plu['timestamp'] = df_plu['timestamp'].dt.tz_localize('UTC')

#     df_plu['timestamp'] = df_plu['timestamp'].dt.tz_convert('America/Sao_Paulo')

#     # df_flu['timestamp'] = pd.to_datetime(df_flu['timestamp'], errors='coerce')
#     if df_flu is not None and not df_flu.empty and 'timestamp' in df_flu.columns:
#         df_flu['timestamp'] = pd.to_datetime(df_flu['timestamp'], errors='coerce')
#     else:
#         print("⚠️ df_flu vazio - pulando timestamp")

#     # if df_flu['timestamp'].dt.tz is None:
#     #     df_flu['timestamp'] = df_flu['timestamp'].dt.tz_localize('UTC')
#     if (
#         df_flu is not None and
#         not df_flu.empty and
#         'timestamp' in df_flu.columns and
#         pd.api.types.is_datetime64_any_dtype(df_flu['timestamp'])
#     ):
#         if df_flu['timestamp'].dt.tz is None:
#             df_flu['timestamp'] = df_flu['timestamp'].dt.tz_localize('UTC')

#     # df_flu['timestamp'] = df_flu['timestamp'].dt.tz_convert('America/Sao_Paulo')
#     if (
#         df_flu is not None and
#         not df_flu.empty and
#         'timestamp' in df_flu.columns
#     ):
#         df_flu['timestamp'] = df_flu['timestamp'].dt.tz_convert('America/Sao_Paulo')

#     df_flu = safe_lower_columns(df_flu)
#     df_plu = safe_lower_columns(df_plu)

#     if df_flu is not None and not df_flu.empty:
#         df_flu.columns = df_flu.columns.astype(str).str.lower()

#     if 'timestamp' not in df_plu.columns:
#         df_plu = df_plu.reset_index()

#     if 'timestamp' not in df_flu.columns:
#         df_flu = df_flu.reset_index()

#     # print("PLU timestamps:", df_plu['timestamp'].head())
#     # print("FLU timestamps:", df_flu['timestamp'].head())    
    
#     df_combined = pd.merge(df_plu, df_flu, on='timestamp', how='outer')
#     return df_combined