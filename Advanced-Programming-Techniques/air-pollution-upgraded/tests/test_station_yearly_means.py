import sys
import os
import pytest
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from station_yearly_means import calculate_monthly_means

@pytest.fixture
def mock_data():
    index = pd.to_datetime(['2020-01-01 01:00:00', '2020-01-01 02:00:00', '2020-01-01 06:00:00',
                             '2020-07-05 05:00:00', '2020-07-05 06:00:00', '2025-10-12 00:00:00'
                             ])
    return pd.DataFrame(
        {
            "Warszawa_StacjaAw": [10.01, 11.02, 12.03, 13.04, 14.05, 15.06],
            "Katowice_StacjaAk": [1, 1, 1, 1, 1, 1],
            "Warszawa_StacjaBw": [0, 1, 2, 3, 4, 5]
        },
        index=index
    )

# Checks if the result is of type pd.DataFrame and if the index was formatted to the correct date type
def test_data_type_and_index_correctness(mock_data):
    result = calculate_monthly_means(mock_data, years=[2020], is_city=True)

    assert isinstance(result, pd.DataFrame)
    assert isinstance(result.index, pd.PeriodIndex)
    assert result.index.freqstr == 'M'

# Checks if parsing column names works correctly for cities
def test_city_differentiation(mock_data):
    result = calculate_monthly_means(mock_data, years=[2020], is_city=True)

    assert set(result.columns) == {"Katowice", "Warszawa"}

# Checks if parsing column names works correctly for stations
def test_station_differentiation(mock_data):
    result = calculate_monthly_means(mock_data, years=[2020], is_city=False)

    assert set(result.columns) == {"StacjaAw", "StacjaAk", "StacjaBw"}

# Checks if the monthly average values are calculated correctly
def test_monthly_averages(mock_data):
    result = calculate_monthly_means(mock_data, years=[2020], is_city=True)

    assert result.loc["2020-07", "Katowice"] == 1 # (1+1)/2 = 1
    assert result.loc["2020-01", "Warszawa"] == ((10.01 + 11.02 + 12.03) + (0 + 1 + 2))/6

# Checks if limiting the year range works correctly
def test_year_range(mock_data):
    result = calculate_monthly_means(mock_data, years=[2025], is_city=True)

    assert all(result.index.year == 2025)

# Checks if providing an empty/incorrect period returns a DataFrame filled with pd.NA
def test_empty_year_range(mock_data):
    result = calculate_monthly_means(mock_data, years=[2022], is_city=True)

    assert result.isna().all().all()