# %%
import json
import os

import numpy as np
import pandas as pd
import psycopg2
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

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

# Preprocessing functions
def delete_nan_target_rows(df, target_variable):
    df = df.dropna(subset=[target_variable])
    return df
def remove_rows_with_nans(df: pd.DataFrame, station_target: str, n_lags: int, max_nans: int):
    """
    Remove rows from the DataFrame where at least `max_nans` values are NaN for the specified columns.
    :param df: input DataFrame
    :param station_target: target station identifier
    :param n_lags: number of lags
    :param max_nans: maximum number of NaN values allowed
    :return: DataFrame with rows removed
    """
    # Generate the column names to check for NaNs
    columns_to_check = [f'flu_{station_target}(t-{i})' for i in range(n_lags)]
    
    # Drop rows where at least `max_nans` values are NaN in the specified columns
    df = df.dropna(subset=columns_to_check, thresh=len(columns_to_check) - max_nans)
    
    return df

def fill_missing_values_horizontal(df: pd.DataFrame, station_prefix: str, n_lags: int):
    """
    Fill missing values for each group of columns related to a station horizontally.
    :param df: input DataFrame
    :param station_prefix: prefix of the station columns (e.g., 'plu_' or 'flu_')
    :param n_lags: number of lags
    :return: DataFrame with missing values filled
    """
    station_columns = [col for col in df.columns if col.startswith(station_prefix)]
    
    for station in set(col.split('(')[0] for col in station_columns):
        cols = [f'{station}(t-{i})' for i in range(n_lags)]
        
        # Interpolate missing values horizontally
        df[cols] = df[cols].interpolate(method='linear', axis=1, limit_direction='both')
        
        # Fill remaining NaNs with backfill and forward fill horizontally
        df[cols] = df[cols].bfill(axis=1).ffill(axis=1)
        
        # Fill rows with all NaNs with zero
        df[cols] = df[cols].fillna(0)
    
    return df

# Functions for training
def split_train_val_test(df, target_variable, test_size=0.2, val_size=0.2):
    X = df.drop(columns=['timestamp', target_variable])
    y = df[target_variable]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=val_size, shuffle=False)
    
    return X_train, X_val, X_test, y_train, y_val, y_test

def train_xgboost(X_train, y_train, X_val, y_val, params):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    
    model = xgb.train(params, dtrain, num_boost_round=1000, evals=[(dtrain, 'train'), (dval, 'val')], early_stopping_rounds=10)
    
    return model

def predict_xgboost(model, X_test):
    dtest = xgb.DMatrix(X_test)
    y_pred = model.predict(dtest)
    
    return y_pred

def save_model_to_db(model, station, horizon, params, period, rmse, db_url):
    # Salvar o modelo em um arquivo temporário
    temp_model_file = 'temp_model.xgb'
    model.save_model(temp_model_file)
    
    # Ler o conteúdo do arquivo binário
    with open(temp_model_file, 'rb') as file:
        model_binary = file.read()
    
    # Conectar ao banco de dados PostgreSQL
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Inserir o modelo no banco de dados
    cursor.execute("""
    INSERT INTO prediction.model (station, horizon, model, main, parameters, period, rmse)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (station, horizon, model_binary, False, json.dumps(params), period, json.dumps(rmse)))
    
    # Commit e fechar a conexão
    conn.commit()
    cursor.close()
    conn.close()
    
    # Remover o arquivo temporário
    os.remove(temp_model_file)

def load_model_from_db(station, horizon, db_url):
    # Conectar ao banco de dados PostgreSQL
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Buscar o modelo do banco de dados
    cursor.execute("SELECT model, parameters, period, rmse FROM prediction.model WHERE station = %s AND horizon = %s", (station, horizon))
    result = cursor.fetchone()
    model_binary = result[0]
    parameters = result[1] if isinstance(result[1], dict) else json.loads(result[1])
    period = result[2]
    rmse = result[3] if isinstance(result[3], dict) else json.loads(result[3])
    
    # Salvar o conteúdo binário em um arquivo temporário
    temp_model_file = 'temp_model.xgb'
    with open(temp_model_file, 'wb') as file:
        file.write(model_binary)
    
    # Carregar o modelo do arquivo temporário
    model = xgb.Booster()
    model.load_model(temp_model_file)
    
    # Remover o arquivo temporário
    os.remove(temp_model_file)
    
    # Fechar a conexão
    cursor.close()
    conn.close()
    
    return model, parameters, period, rmse

# %%
# Example
# Load data
start_time = '2022-01-01'
end_time = '2022-06-01'
period = f'{start_time} to {end_time}'
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
station_target = '413'
target_variable = f'flu_{station_target}(t+{horizon-1})'
max_nans = 3
embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
# %%
# Preprocessing steps
embedded_df = delete_nan_target_rows(embedded_df, f'flu_{station_target}(t+{horizon-1})')
embedded_df = remove_rows_with_nans(embedded_df, station_target, n_lags, max_nans)
embedded_df
# %%
# Preencher valores ausentes para colunas de chuva
embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
# Preencher valores ausentes para colunas de nível
embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)

# %% Training

X_train, X_val, X_test, y_train, y_val, y_test = split_train_val_test(embedded_df, target_variable)
params = {
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'eta': 0.1,
    'max_depth': 6,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'seed': 42
}

# Treinar o modelo XGBoost
model = train_xgboost(X_train, y_train, X_val, y_val, params)

# Fazer previsões no conjunto de teste
y_pred = predict_xgboost(model, X_test)

# Calcular o erro quadrático médio
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f'RMSE: {rmse}')
rmse = {
    'train': np.sqrt(mean_squared_error(y_train, model.predict(xgb.DMatrix(X_train)))),
    'val': np.sqrt(mean_squared_error(y_val, model.predict(xgb.DMatrix(X_val)))),
    'test': np.sqrt(mean_squared_error(y_test, model.predict(xgb.DMatrix(X_test))))
}
# %%
# Plotar o predito e o real com plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_predictions(y_true, y_pred, title='Predictions vs True values', x_label='Timestamp', y_label='Value'):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(len(y_true)), y=y_true, mode='lines', name='True values'))
    fig.add_trace(go.Scatter (x=np.arange(len(y_pred)), y=y_pred, mode='lines', name='Predictions'))
    fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label)
    fig.show()
plot_predictions(y_test, y_pred)

# %% Save model in the database
DATABASE_URL = os.getenv("DATABASE_URL")
save_model_to_db(model, station_target, horizon, params, period, rmse, DATABASE_URL)

# %%
model = load_model_from_db(station_target, horizon, DATABASE_URL)
model, parameters, period, rmse = load_model_from_db(station_target, horizon, DATABASE_URL)    
# Fazer previsões no conjunto de teste
dtest = xgb.DMatrix(X_test)
y_pred = model.predict(dtest)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f'RMSE: {rmse}')
# %%
