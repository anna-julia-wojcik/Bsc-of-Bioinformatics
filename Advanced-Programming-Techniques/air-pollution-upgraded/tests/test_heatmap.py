import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from heatmap import prepare_heatmap_data, create_heatmap
years = [2015, 2018, 2021, 2024]

@pytest.fixture
def mock_data():
    index = pd.to_datetime([
        '2015-01-01 00:00:00', '2015-01-01 01:00:00',
        '2018-06-15 12:00:00', '2018-06-15 13:00:00',
        '2021-03-10 10:00:00',
        '2024-12-31 23:00:00'
    ])
    return pd.DataFrame({
        'Miejscowość_Kod stacji': index,
        "Warszawa_Stacja1": [10, 20, 30, 40, 50, 60],
        "Warszawa_Stacja2": [0, 10, 20, 30, 40, 50],
        "Krakow_Stacja1": [100, 100, 100, 100, 100, 100]
    })


def test_result_type_and_columns(mock_data: pd.DataFrame):
    # Check if the result is of type pd.DataFrame and has the correct columns
    result = prepare_heatmap_data(mock_data)

    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {"Rok", "Miesiąc", "Miasto", "PM2.5"}


def test_correctness_of_dates_in_result(mock_data: pd.DataFrame):
    # Check if years and months are correctly extracted as numbers
    result = prepare_heatmap_data(mock_data)

    assert set(result['Rok'].unique()) == {2015, 2018, 2021, 2024}
    assert set(result['Miesiąc'].unique()) == {1, 3, 6, 12}
    assert np.issubdtype(result['Rok'].dtype, np.integer)


def test_city_grouping_mean(mock_data: pd.DataFrame):
    # Check if stations from the same city are correctly averaged
    result = prepare_heatmap_data(mock_data)

    # Check Warsaw for the year 2015
    # Stacja1 mean (10+20)/2 = 15
    # Stacja2 mean (0+10)/2 = 5
    # City mean: (15+5)/2 = 10
    warsaw_2015 = result[(result['Miasto'] == 'Warszawa') & (result['Rok'] == 2015)]

    assert warsaw_2015['PM2.5'].iloc[0] == 10.0


def test_correct_index_removal(mock_data: pd.DataFrame):
    # Check if the index column was actually removed from the DataFrame
    result = prepare_heatmap_data(mock_data)

    assert 'Miejscowość_Kod stacji' not in result.columns


def test_heatmap_unique_cities(mock_data: pd.DataFrame):
    # Check if the function correctly identifies cities to be drawn on the heatmap
    df_long = prepare_heatmap_data(mock_data)
    unique_cities = sorted(df_long['Miasto'].unique())

    assert unique_cities == ["Krakow", "Warszawa"]