# %%
import argparse
import os
import psycopg2
from dotenv import load_dotenv

import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt

from dateutil.relativedelta import relativedelta

import time

from scripts.database import save_model_to_db
from scripts.preprocess import (delete_nan_target_rows,
                                fill_missing_values_horizontal,
                                remove_rows_with_nans)
from scripts.time_delay_embedding import time_delay_embedding_df
from scripts.train import predict_xgboost, split_train_val_test, train_xgboost
from scripts.utils import load_data
from sklearn.metrics import mean_squared_error

if __name__ == "__main__":
    load_dotenv()

    start_time = time.time()
    print(f"Início do script: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    parser = argparse.ArgumentParser(description='Train and save XGBoost model.')
    parser.add_argument('--horizon', type=int, default=10, help='Horizon for time delay embedding')
    args = parser.parse_args()

    horizon = args.horizon

# %%
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# %%
# 1. Buscar estações flu
cursor.execute("SELECT original_id, name FROM station.station_flu")
stations_flu = cursor.fetchall()

station_name_flu = [row[1] for row in stations_flu]
station_code_map = {row[1]: row[0] for row in stations_flu}

print(station_name_flu)
print(station_code_map.get('Rio Tamanduateí - Mercado Municipal'))

station_name_flu = ['Rio Tamanduateí - Mercado Municipal']
station_code = station_code_map.get(station_name_flu[0])

# %%
# 3. Buscar período global
cursor.execute("""
SELECT MIN(timestamp), MAX(timestamp)
FROM timeseries.data_station_flu
WHERE station = %s
""", (station_code,))
min_date, max_date = cursor.fetchone()

# usar últimos 6 meses
min_date = max_date - relativedelta(months=6)
end_datetime = max_date

# período dos dados
start_date_str = min_date.strftime('%Y-%m-%d')
end_date_str = max_date.strftime('%Y-%m-%d')

period = f"{start_date_str} to {end_date_str}"

# %%
# 4. Carregar dados (mantido)
print('Loading data...')
df = load_data(min_date, max_date, station_name_flu)
print(f'Data shape: {df.shape}')

# %%
# Aplicar Time Delay Embedding (mantido)
n_lags = 6
horizon = args.horizon

# Mantido: uma estação alvo (igual ao original)
station_target = str(station_code_map[station_name_flu[0]])

# print(station_target)

print("="*50)
print(f"Horizon: {horizon}")
print(f"Station: {station_target}")
print(f"Período: {period}")
print("="*50)

target_variable = f'flu_{station_target}(t+{horizon})'
max_nans = 3

embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
embedded_df.sort_index(inplace=True)

# Preprocessing (mantido)
embedded_df = delete_nan_target_rows(embedded_df, target_variable)
embedded_df = remove_rows_with_nans(embedded_df, station_target, n_lags, max_nans)
embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)

embedded_df = embedded_df.drop(columns=[
    col for col in embedded_df.columns if 'timestamp' in col
])

# %%
# Split (mantido)
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

# %%
# Treino (mantido)
model, evals_result = train_xgboost(X_train, y_train, X_val, y_val, params)

y_pred = predict_xgboost(model, X_test)

rmse = {
    'train': np.sqrt(mean_squared_error(y_train, model.predict(xgb.DMatrix(X_train)))),
    'val': np.sqrt(mean_squared_error(y_val, model.predict(xgb.DMatrix(X_val)))),
    'test': np.sqrt(mean_squared_error(y_test, model.predict(xgb.DMatrix(X_test))))
}

# %%
# Salvar modelo (mantido)
save_model_to_db(model, station_target, horizon, params, period, rmse, DATABASE_URL)

# %%
# Fechar conexão
cursor.close()
conn.close()

end_time = time.time()

print("="*50)
print(f"RMSE: {rmse}")
print(f"Tempo total: {end_time - start_time:.2f}s")
print("="*50)

train_rmse = evals_result['train']['rmse']
val_rmse = evals_result['val']['rmse']

plt.plot(train_rmse, label='Train RMSE')
plt.plot(val_rmse, label='Val RMSE')
plt.xlabel('Iterações')
plt.ylabel('RMSE')
plt.legend()
plt.title('Curva de treino')
plt.show()

print(f"Melhor iteração: {model.best_iteration}")
print(f"Melhor score (val): {model.best_score}")

print(evals_result['train'].keys())
print(evals_result['val'].keys())

print(train_rmse[:10])
print(val_rmse[:10])