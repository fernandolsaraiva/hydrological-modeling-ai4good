import os
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shap
import streamlit as st
import xgboost as xgb
from PIL import Image
from sklearn.metrics import mean_squared_error

from src.scripts.database import load_model_from_db
from src.scripts.preprocess import fill_missing_values_horizontal
from src.scripts.time_delay_embedding import time_delay_embedding_df
from src.scripts.utils import load_data
from util import get_station_code_flu, get_station_names


def plot_predictions(y_test, y_pred, timestamps):
    fig = go.Figure()

    # Add actual values line
    fig.add_trace(go.Scatter(x=timestamps, y=y_test, mode='lines+markers', name='Actual Values', line=dict(color='blue')))

    # Add predicted values line
    fig.add_trace(go.Scatter(x=timestamps, y=y_pred, mode='lines+markers', name='Predicted Values', line=dict(color='orange')))

    # Configure layout of the plot
    fig.update_layout(
        title='Comparison between Actual and Predicted Values',
        xaxis_title='Timestamp',
        yaxis_title='Values',
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, t=30, b=0)
    )

    # Display the plot using Streamlit
    st.plotly_chart(fig)

if __name__ == "__main__":
    logo = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo, width=200)
    logo = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo, width=150)
    st.title('Historical Data and Predictions')

    station_names = get_station_names()
    default_station = 'Rio Tamanduateí - Mercado Municipal'
    if default_station in station_names:
        station_name = st.selectbox('Select the station', station_names, index=station_names.index(default_station))
    else:
        station_name = st.selectbox('Select the station', station_names)

    col1, col2 = st.columns(2)

    with col1:
        start_time = st.date_input("Choose the start date", value=pd.to_datetime('today').date() - timedelta(days=7))

    with col2:
        end_time = st.date_input("Choose the end date", value=pd.to_datetime('today').date())

    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)
    horizon = st.selectbox('Choose the horizon', list(range(1, 13)), index=5)

    if st.button('Plot'):
        station_code = get_station_code_flu(station_name)

        df = load_data(start_time, end_time)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/Sao_Paulo')
        df= df.sort_values(by='timestamp', ascending=False)
        df.set_index('timestamp', inplace=True)

        # Carregar modelo do banco
        DATABASE_URL = os.getenv("DATABASE_URL")
        model, parameters, period, rmse = load_model_from_db(station_code, horizon, DATABASE_URL)

        # Aplicar Time Delay Embedding
        n_lags = 6
        horizon = horizon
        station_target = station_code
        target_variable = f'flu_{station_target}(t+{horizon})'
        max_nans = 3
        embedded_df = time_delay_embedding_df(df, n_lags, horizon, station_target=station_target)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'plu_', n_lags)
        embedded_df = fill_missing_values_horizontal(embedded_df, 'flu_', n_lags)
        X_test = embedded_df.drop(columns=[target_variable])
        y_test = embedded_df[target_variable]
        d_test = xgb.DMatrix(X_test)
        y_pred = model.predict(d_test)
        adjusted_timestamps = X_test.index - pd.to_timedelta(horizon * 10, unit='m')

        # Remover valores NaN de y_test e y_pred
        mask = ~np.isnan(y_test) & ~np.isnan(y_pred)
        y_test_filtered = y_test[mask]
        y_pred_filtered = y_pred[mask]
        adjusted_timestamps_filtered = adjusted_timestamps[mask]
        rmse = np.sqrt(mean_squared_error(y_test_filtered, y_pred_filtered))
        st.write(f'RMSE: {rmse}')

        plot_predictions(y_test_filtered, y_pred_filtered, adjusted_timestamps_filtered)

        # Shap value analysis
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(d_test)

        # Convert SHAP values to a DataFrame
        shap_values_df = pd.DataFrame(shap_values, columns=X_test.columns)

        # Add the feature values to the DataFrame
        for col in X_test.columns:
            shap_values_df[col + '_value'] = X_test[col].values

        # Melt the DataFrame to long format
        shap_values_long = shap_values_df.melt(id_vars=[col + '_value' for col in X_test.columns], 
                                            var_name='Feature', value_name='SHAP Value')

        # Extract the feature name and value
        shap_values_long['Feature'] = shap_values_long['Feature'].str.replace('_value', '')
        shap_values_long['Feature Value'] = shap_values_long.apply(lambda row: row[row['Feature'] + '_value'], axis=1)

        # Create a beeswarm plot using Plotly
        fig = px.scatter(shap_values_long, x='SHAP Value', y='Feature', color='Feature Value',
                        color_continuous_scale='RdBu', title='SHAP Beeswarm Plot')

        # Display the plot in Streamlit
        st.plotly_chart(fig)
            
                