# The Second Project: Energy Consumption Prediction

The project is a Jupyter Notebook-based analysis pipeline that integrates household energy consumption data with meteorological data to build and evaluate regression models for daily power usage forecasting. Two models are compared — linear regression and 2nd degree polynomial regression — with the better-performing model exposed via a FastAPI prediction endpoint.

## My Contribution

I was responsible for Part 3 and Part 4, which involved designing and implementing the full model training pipeline, including the `split_train_test` function for time-series-aware data splitting, `linear_regression` and `polynomial_regression_degree_2` for training and evaluating both models, and `compare_results` for presenting the metrics side by side. I also built the FastAPI integration in Task 4, defining the `DailyFeatures` Pydantic schema, the `lifespan` context manager for model loading at startup, and the `predict_consumption` endpoint at `POST /predict_daily_consumption`.

## Project Stages

- Downloading and preprocessing household power consumption data from a public dataset.
- Fetching historical hourly weather data (temperature, precipitation, wind speed) from the Open-Meteo archive API.
- Merging both datasets on a shared datetime index, cleaning missing values, and resampling to daily aggregates.
- Training and evaluating linear and polynomial regression models.
- Exposing predictions through a FastAPI REST endpoint.

## Installation and Requirements

The project requires Python ≥ 3.8. Install all dependencies with:

```bash
pip install pandas requests scikit-learn joblib fastapi pydantic uvicorn
```

# Running the Notebook

## Execution

Open and run the notebook cell by cell in order:

```bash
jupyter notebook energy_consumption_prediction.ipynb
```

Tasks 1 and 2 handle data acquisition and preprocessing. Tasks 3 and 4 handle model training and the API definition. All cells must be executed in sequence, as each task depends on the outputs of the previous one.

## Data Sources

The notebook automatically fetches data from two external sources:

- **Energy data**: UCI Household Power Consumption dataset (downloaded as a `.zip` via direct URL)
- **Weather data**: Open-Meteo Historical Archive API for coordinates `48.85°N, 2.35°E` (Sceaux, France), covering `2006-12-16` to `2010-11-26`

No manual data download is required.

# Task Descriptions

## Task 1 — Data Loading and Merging

### Input:
- Household Power Consumption dataset (CSV inside ZIP, semicolon-separated)
- Open-Meteo archive API (hourly: `temperature_2m`, `precipitation`, `wind_speed_10m`)

### Output:
- `df_energy` — energy DataFrame indexed by `Datetime`
- `df_weather` — weather DataFrame indexed by `Datetime`
- `df_combined` — merged DataFrame (left join on `Datetime`)

### Logic:

1. Loads energy data from the remote ZIP, parses `Date` and `Time` columns into a single `Datetime` index, and converts all measurement columns to `float64`.
2. Fetches hourly weather data for the matching date range and sets `Datetime` as the index.
3. Joins both DataFrames on the `Datetime` index into `df_combined`.

## Task 2 — Cleaning and Daily Aggregation

### Input:
- `df_combined` — merged hourly DataFrame

### Output:
- `df_daily` — cleaned daily DataFrame (1433 rows)

### Logic:

1. Drops all rows containing `NaN` values.
2. Resamples the cleaned data to daily frequency using the following aggregation strategy:
   - `sum` for power and sub-metering columns (`Global_active_power`, `Global_reactive_power`, `Sub_metering_1`, `Sub_metering_2`, `Sub_metering_3`, `precipitation`)
   - `mean` for voltage, intensity, temperature, and wind speed
3. Drops any remaining `NaN` rows after resampling.

## Task 3 — Model Training and Evaluation

### Input:
- `df_daily` — daily aggregated DataFrame

### Output:
- `linear_model.pkl` — saved linear regression model
- `polynomial_model.pkl` — saved polynomial regression model
- `polynomial_transformer.pkl` — saved polynomial feature transformer
- Printed MSE and R² metrics for both models

### Functions:

**`split_train_test(df)`**
Splits the daily DataFrame into training (80%) and test (20%) sets without shuffling, preserving time series order. The dependent variable is `Global_active_power`; the 9 independent variables are the remaining energy and weather features.

**`linear_regression(x_train, y_train, x_test, y_test)`**
Trains a `LinearRegression` model, evaluates it on the test set (MSE and R²), and saves the model to `linear_model.pkl`.

**`polynomial_regression_degree_2(x_train, y_train, x_test, y_test)`**
Transforms features using `PolynomialFeatures(degree=2, include_bias=False)`, trains a `LinearRegression` model on the expanded features, evaluates it, and saves both the transformer and model to `.pkl` files.

**`compare_results(linear_results, polynomial_results)`**
Prints MSE and R² for both models side by side.

### Results:

| Model | MSE | R² |
|---|---|---|
| Linear Regression | 4.980 | 0.925 |
| Polynomial Regression (degree 2) | 1.744 | 0.974 |

The polynomial regression model performs significantly better — it has a much lower MSE and explains nearly 5% more variance in the data.

## Task 4 — FastAPI Prediction Endpoint

### Input:
- Saved model files: `linear_model.pkl`, `polynomial_model.pkl`, `polynomial_transformer.pkl`
- A JSON request body with 9 daily feature values

### Output:
- A prediction of daily energy consumption (kW) from both models
- A recommendation noting the polynomial model as superior

### Logic:

Models are loaded at application startup via the `lifespan` async context manager into global variables. If loading fails, the models are set to `None`.

The `DailyFeatures` Pydantic model validates the 9 input fields:

| Field | Description | Unit |
|---|---|---|
| `temperature_2m` | Average daily temperature | °C |
| `precipitation` | Total daily precipitation | mm |
| `wind_speed_10m` | Average daily wind speed | km/h |
| `global_reactive_power` | Daily sum of reactive power | kW |
| `voltage` | Average daily voltage | V |
| `global_intensity` | Average daily current intensity | A |
| `sub_metering_1` | Daily sub-meter 1 consumption | Wh |
| `sub_metering_2` | Daily sub-meter 2 consumption | Wh |
| `sub_metering_3` | Daily sub-meter 3 consumption | Wh |

The endpoint `POST /predict_daily_consumption` returns forecasts from both models and a recommendation. It raises HTTP 500 if the models were not loaded correctly.

### Running the API server:

Due to the single-notebook constraint of the project, the FastAPI app is defined but not launched inline. To run it outside the notebook:

```bash
uvicorn notebook_module:app --reload
```

The API will then be available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.
