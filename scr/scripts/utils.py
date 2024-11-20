# %%
import os
import sys

# Adiciona o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import pandas as pd

from util import (get_station_code, get_station_data_flu, get_station_data_plu,
                  get_station_names_plu)


# %%
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
        
        # Certifique-se de que ambos os DataFrames tenham o mesmo tipo de índice de data e hora
        if df.empty:
            df = station_data
        else:
            # Converta ambos os índices para o mesmo fuso horário ou remova o fuso horário de ambos
            if df.index.tz is None:
                station_data.index = station_data.index.tz_localize(None)
            else:
                station_data.index = station_data.index.tz_convert(df.index.tz)
            
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
        
        # Certifique-se de que ambos os DataFrames tenham o mesmo tipo de índice de data e hora
        if df.empty:
            df = station_data
        else:
            # Converta ambos os índices para o mesmo fuso horário ou remova o fuso horário de ambos
            if df.index.tz is None:
                station_data.index = station_data.index.tz_localize(None)
            else:
                station_data.index = station_data.index.tz_convert(df.index.tz)
            
            df = pd.merge(df, station_data, on='timestamp', how='outer')
    return df

def load_data(start_time, end_time, station_name_flu=['Rio Tamanduateí - Mercado Municipal']):
    df_plu = load_pluviometric_data(start_time, end_time)
    df_flu = load_fluviometric_data(start_time, end_time, station_name_flu)
    df_combined = pd.merge(df_plu, df_flu, on='timestamp', how='outer')
    return df_combined