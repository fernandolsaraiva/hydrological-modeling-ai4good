import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Abaixo quero fazer um import da função get_station_data do script 1_Hydrological_Monitoring e por o nome de get_station_data_flu


from get_station_data import get_station_data  # Assuming this function is available in your repo

class HydrologicalModel:
    def __init__(self, start_time, end_time, lags, model_type='xgboost'):
        self.start_time = start_time
        self.end_time = end_time
        self.lags = lags
        self.model_type = model_type
        self.model = None

    def fetch_data(self):
        # Fetch data from the database using the provided function
        river_data = get_station_data('river', self.start_time, self.end_time)
        rain_data = get_station_data('rain', self.start_time, self.end_time)
        return river_data, rain_data

    def create_features(self, river_data, rain_data):
        # Create lagged features for river and rain data
        for lag in range(1, self.lags + 1):
            river_data[f'river_lag_{lag}'] = river_data['level'].shift(lag)
            for station in rain_data.columns:
                rain_data[f'{station}_lag_{lag}'] = rain_data[station].shift(lag)
        
        # Drop rows with NaN values due to lagging
        river_data = river_data.dropna()
        rain_data = rain_data.dropna()
        
        # Merge river and rain data on the timestamp
        data = pd.merge(river_data, rain_data, left_index=True, right_index=True)
        return data

    def prepare_data(self, data):
        # Split data into features and target
        X = data.drop(columns=['level'])
        y = data['level']
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train):
        if self.model_type == 'xgboost':
            self.model = xgb.XGBRegressor()
        else:
            raise ValueError("Unsupported model type")
        
        self.model.fit(X_train, y_train)

    def run(self):
        river_data, rain_data = self.fetch_data()
        data = self.create_features(river_data, rain_data)
        X_train, X_test, y_train, y_test = self.prepare_data(data)
        self.train_model(X_train, y_train)
        print(f"Model trained with {self.model_type}")

# Example usage
if __name__ == "__main__":
    model = HydrologicalModel(start_time='2020-01-01', end_time='2021-01-01', lags=3, model_type='xgboost')
    model.run()