# Floodcasting XAI Alert System

This project is an operational tool for predicting urban floods using explainable Artificial Intelligence (XAI). It uses open-source tools, real-time execution, a user-friendly interface, and a scalable approach. The project is supported by the AI4Good Brazil Conference.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/fernandolsaraiva/hydrological-modeling-ai4good.git
    cd hydrological-modeling-ai4good
    ```

2. Create and activate a virtual environment:
    ```sh
    conda create -n ai4good python==3.11
    conda activate ai4good
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Set up the environment variables by creating a `.env` file with the following content:
    ```env
    DATABASE_URL=database_url
    ```

Note: The database is in read-only mode. You can view the data but cannot make any modifications.

2. Run the Streamlit application:
    ```sh
    streamlit run Home.py
    ```

In production, the application is available at www.floodcastingxai.com


3. To run the scraper:
    ```sh
    python scraper.py
    ```

### Hosting Information

Our entire infrastructure is hosted on Heroku. This includes our PostgreSQL database, our main Streamlit application, and even our scraper, which runs continuously. Heroku provides a reliable and scalable cloud platform for our needs. Additionally, Heroku leverages AWS (Amazon Web Services) to ensure high availability and performance.

## Project Structure
```
. 
├── aux/ │ 
    ├── insert_critical_levels.py 
    ├── insert_stations.py 
├── data/ 
    ├── stations_flu.csv 
    ├── stations_plu.csv 
├── img/ 
├── pages/ 
    ├── 1_Real_Time_Forecasting.py 
    ├── 2_Historical_Data_and_Predictions.py 
    ├── 3_Hydrological_Monitoring.py
    ├── 4_Rainfall_Monitoring.py 
    ├── 5_About_Us.py 
├── src/ 
    ├── data/ 
        ├── data_experimental.csv │ 
    ├── scripts/ │ 
        ├── database.py │ 
        ├── preprocess.py │ 
        ├── time_delay_embedding.py │ 
        ├── train.py │ 
        ├── utils.py 
        ├── main.py 
├── .env 
├── .gitignore 
├── .slugignore 
├── Procfile 
├── README.md 
├── requirements.txt 
├── runtime.txt 
├── scraper.py 
├── util.py
```

## Key Components

### Data Processing

- `src/scripts/preprocess.py`: Contains functions for preprocessing data, such as deleting rows with NaN values and filling missing values.
- `src/scripts/time_delay_embedding.py`: Implements time delay embedding for time series data, so that we can convert the time series structure into an tabular structure.

### Model Training and Prediction

- `src/scripts/train.py`: Contains functions for training and predicting with XGBoost models. It is possible to customize with new station names and codes, as well as the horizons, to train new models and save them to the database. In the future, we plan to introduce the capability to train new models (such as LightGBM and CatBoost).
- `src/scripts/database.py`: Functions for saving and loading models from the database.

### Data Handling

- `scraper.py`: Script for downloading and upserting data from external sources.
- `util.py`: Utility functions for interacting with the database and fetching station data.

### Streamlit Pages

- `pages/1_Real_Time_Forecasting.py`: Real-time forecasting interface. Users can select the station, the prediction time (current or a past moment), and obtain the prediction for a time horizon. Additionally, users can choose any point in the prediction to get an explainability analysis of that point using SHAP values.
- `pages/2_Historical_Data_and_Predictions.py`: Historical data and predictions interface. Users can select any period in the past and choose the prediction model to view the predictions. Each model is trained for a specific time horizon (e.g., 10 minutes, 20 minutes, etc.). Users can view the predictions and the SHAP values analysis.
- `pages/3_Hydrological_Monitoring.py`: Hydrological monitoring interface. Users can select the station, the desired period, and the type of aggregation (10-minute, hourly, or daily) to view segments of the river level time series.
- `pages/4_Rainfall_Monitoring.py`: Rainfall monitoring interface. Users can select the station, the desired period, and the type of aggregation (10-minute, hourly, or daily) to view segments of the rainfall level time series.
- `pages/5_About_Us.py`: Information about the team.

### Auxiliary Scripts

- `aux/insert_critical_levels.py`: Script to insert critical levels into the database.
- `aux/insert_stations.py`: Script to insert station data into the database.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.