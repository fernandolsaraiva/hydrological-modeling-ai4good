import json
import os

import psycopg2
import xgboost as xgb


def save_model_to_db(model, station, horizon, params, period, rmse, db_url):
    temp_model_file = 'temp_model.xgb'
    model.save_model(temp_model_file)
    with open(temp_model_file, 'rb') as file:
        model_binary = file.read()
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO prediction.model (station, horizon, model, main, parameters, period, rmse)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (station, horizon, model_binary, False, json.dumps(params), period, json.dumps(rmse)))
    conn.commit()
    cursor.close()
    conn.close()
    os.remove(temp_model_file)

def load_model_from_db(station, horizon, db_url):
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT model, parameters, period, rmse FROM prediction.model WHERE station = %s AND horizon = %s", (station, horizon))
    result = cursor.fetchone()
    model_binary = result[0]
    parameters = result[1] if isinstance(result[1], dict) else json.loads(result[1])
    period = result[2]
    rmse = result[3] if isinstance(result[3], dict) else json.loads(result[3])
    temp_model_file = 'temp_model.xgb'
    with open(temp_model_file, 'wb') as file:
        file.write(model_binary)
    model = xgb.Booster()
    model.load_model(temp_model_file)
    os.remove(temp_model_file)
    cursor.close()
    conn.close()
    return model, parameters, period, rmse

def load_all_models_from_db(station_code, DATABASE_URL):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT horizon, model, parameters, period, rmse FROM prediction.model WHERE station = %s and main = TRUE", (station_code,))
    results = cursor.fetchall()
    
    models = []
    for result in results:
        horizon = result[0]
        model_binary = result[1]
        parameters = result[2] if isinstance(result[2], dict) else json.loads(result[2])
        period = result[3]
        rmse = result[4] if isinstance(result[4], dict) else json.loads(result[4])
        
        temp_model_file = f'temp_model_{horizon}.xgb'
        with open(temp_model_file, 'wb') as file:
            file.write(model_binary)
        
        model = xgb.Booster()
        model.load_model(temp_model_file)
        os.remove(temp_model_file)
        
        models.append((horizon, model, parameters, period, rmse))
    
    cursor.close()
    conn.close()

    models.sort(key=lambda x: x[0])
    return models