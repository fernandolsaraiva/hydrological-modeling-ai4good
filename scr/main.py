# %%
import argparse
import os

import numpy as np
import pandas as pd
import xgboost as xgb
from scripts.database import load_model_from_db, save_model_to_db
from scripts.preprocess import (delete_nan_target_rows,
                                fill_missing_values_horizontal,
                                remove_rows_with_nans)
from scripts.time_delay_embedding import time_delay_embedding_df
from scripts.train import predict_xgboost, split_train_val_test, train_xgboost
from scripts.utils import load_data
from sklearn.metrics import mean_squared_error

# %%
# Configurar argparse para aceitar argumentos de linha de comando
parser = argparse.ArgumentParser(description='Train and save XGBoost model.')
parser.add_argument('--horizon', type=int, default=12, help='Horizon for time delay embedding')
args = parser.parse_args()

# %%
# Exemplo de uso
start_time = '2022-01-01'
end_time = '2022-06-01'
period = f'{start_time} to {end_time}'
station_name_flu = ['Rio Tamanduateí - Mercado Municipal']
load_data_bool = False
if load_data_bool:
    df = load_data(start_time, end_time, station_name_flu)
    df.to_csv('data/data_experimental.csv', index=False)
#df = pd.read_csv('data/data_experimental.csv')
df = pd.read_csv('scr/data/data_experimental.csv')
df.set_index('timestamp', inplace=True)
print(df.head(30))
# %%
# Aplicar Time Delay Embedding
n_lags = 6
horizon = args.horizon
print(horizon)
#horizon = 12
station_target = '413'
target_variable = f'flu_{station_target}(t+{horizon})'
max_nans = 3
embedded_df = time_delay_embedding_df(df, n_lags, horizon, 
station_target=station_target)
embedded_df.sort_index(inplace=True)
print(embedded_df)
# Preprocessing steps
embedded_df = delete_nan_target_rows(embedded_df, target_variable)
embedded_df = remove_rows_with_nans(embedded_df, station_target, n_lags, max_nans)
embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)

# Dividir os dados em conjuntos de treino, validação e teste
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

model = train_xgboost(X_train, y_train, X_val, y_val, params)
y_pred = predict_xgboost(model, X_test)
rmse = {
    'train': np.sqrt(mean_squared_error(y_train, model.predict(xgb.DMatrix(X_train)))),
    'val': np.sqrt(mean_squared_error(y_val, model.predict(xgb.DMatrix(X_val)))),
    'test': np.sqrt(mean_squared_error(y_test, model.predict(xgb.DMatrix(X_test))))
}
print(f'RMSE: {rmse}')
# %%
# Salvar o modelo no banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
save_model_to_db(model, station_target, horizon, params, period, rmse, DATABASE_URL)
# %%
# Carregar o modelo do banco de dados e fazer previsões
# model, parameters, period, rmse = load_model_from_db(station_target, horizon, DATABASE_URL)
# y_pred = predict_xgboost(model, X_test)
# print(f'RMSE: {rmse}')
# %%
