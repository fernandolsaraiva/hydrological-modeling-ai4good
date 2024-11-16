# %%
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split

from util import get_station_data_flu, get_station_data_plu, get_station_names_plu


# %%
station_names_plu = get_station_names_plu()

# %%
# Dado um start_time e end_time, escreva um loop para baixar a série temporal de todas as estações pluviométricas e salvar em um dataframe
start_time = '2024-06-06'
end_time = '2024-06-16'
df = pd.DataFrame()

for station_name in station_names_plu:
    station_data = get_station_data_plu(station_name, start_time, end_time, '10-minute')
    station_code = station_data['station'].iloc[0]
    station_name = 'plu_' + str(station_code)
    station_data = station_data.drop(columns=['station'])
    station_data = station_data.rename(columns={'value': station_name})
    if df.empty:
        df = station_data
    else:
        df = pd.merge(df, station_data, on='timestamp', how='outer')

# %%
# Display the dataframe
print(df)

# %%
