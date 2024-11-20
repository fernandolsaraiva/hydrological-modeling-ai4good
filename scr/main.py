# %%
import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from scripts.preprocess import delete_nan_target_rows, remove_rows_with_nans, fill_missing_values_horizontal
from scripts.train import split_train_val_test, train_xgboost, predict_xgboost
from scripts.database import save_model_to_db, load_model_from_db
from scripts.utils import load_data
from scripts.time_delay_embedding import time_delay_embedding_df
import xgboost as xgb

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

df = pd.read_csv('data/data_experimental.csv')

# Aplicar Time Delay Embedding
n_lags = 6
horizon = 12
station_target = '413'
target_variable = f'flu_{station_target}(t+{horizon})'
max_nans = 3
embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)

# Preprocessing steps
embedded_df = delete_nan_target_rows(embedded_df, target_variable)
embedded_df = remove_rows_with_nans(embedded_df, station_target, n_lags, max_nans)
embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)

# Dividir os dados em conjuntos de treino, validação e teste
X_train, X_val, X_test, y_train, y_val, y_test = split_train_val_test(embedded_df, target_variable)

# Definir os parâmetros do modelo XGBoost
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
model, parameters, period, rmse = load_model_from_db(station_target, horizon, DATABASE_URL)
y_pred = predict_xgboost(model, X_test)
print(f'RMSE: {rmse}')
# %%
