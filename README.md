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
    git clone https://github.com/yourusername/floodcasting-xai-alert-system.git
    cd floodcasting-xai-alert-system
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Set up the environment variables by creating a `.env` file with the following content:
    ```env
    DATABASE_URL=your_database_url
    ```

2. Run the Streamlit application:
    ```sh
    streamlit run Home.py
    ```

3. To run the scraper:
    ```sh
    python scraper.py
    ```

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

- `src/scripts/train.py`: Contains functions for training and predicting with XGBoost models.
- `src/scripts/database.py`: Functions for saving and loading models from the database.

### Data Handling

- `scraper.py`: Script for downloading and upserting data from external sources.
- `util.py`: Utility functions for interacting with the database and fetching station data.

### Streamlit Pages

- `pages/1_Real_Time_Forecasting.py`: Real-time forecasting interface.
- `pages/2_Historical_Data_and_Predictions.py`: Historical data and predictions interface.
- `pages/3_Hydrological_Monitoring.py`: Hydrological monitoring interface.
- `pages/4_Rainfall_Monitoring.py`: Rainfall monitoring interface.
- `pages/5_About_Us.py`: Information about the team.

### Auxiliary Scripts

- `aux/insert_critical_levels.py`: Script to insert critical levels into the database.
- `aux/insert_stations.py`: Script to insert station data into the database.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.