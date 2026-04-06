import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from grouped_barplot import calculate_exceedance_days, top3_exceedances
years = [2015, 2018, 2021, 2024]

@pytest.fixture
def mock_data():
    index = pd.to_datetime([
        '2015-01-01 10:00:00', '2015-01-01 20:00:00',  # Daily mean 20 -> Exceedance (2015)
        '2018-01-01 10:00:00', '2018-01-01 20:00:00',  # Daily mean 5 -> None (2018)
        '2021-01-01 10:00:00', '2021-01-01 20:00:00',  # Daily mean 8 -> None (2021)
        '2024-01-01 10:00:00', '2024-01-01 20:00:00'   # Daily mean 10 -> None (2024)
    ])
    return pd.DataFrame({
        "Miejscowość_Kod stacji": index,
        "Warszawa_S1": [20, 20, 5, 5, 8, 8, 10, 10],
        "Gdansk_S1": [0, 0, 0, 0, 0, 0, 0, 0],
        "Krakow_S1": [100, 100, 100, 100, 100, 100, 100, 100]
    })


def test_result_type_and_years_index(mock_data: pd.DataFrame):
    # Check if the result is of type pd.DataFrame and if the year indices are correct
    result = calculate_exceedance_days(mock_data, years)

    assert isinstance(result, pd.DataFrame)
    assert list(result.index) == [2015, 2018, 2021, 2024]


def test_days_calculation_logic(mock_data: pd.DataFrame):
    # Check if the number of days above 15 is calculated correctly
    result = calculate_exceedance_days(mock_data, years)
    assert result.loc[2015, "Warszawa_S1"] == 1

    # Warsaw should have 1 day in 2015 and 0 in the others
    assert result.loc[2015, "Warszawa_S1"] == 1
    assert result.loc[2018, "Warszawa_S1"] == 0
    assert result.loc[2021, "Warszawa_S1"] == 0
    assert result.loc[2024, "Warszawa_S1"] == 0

    # Gdansk should always have 0
    assert result["Gdansk_S1"].sum() == 0


def test_top3_lists_and_size(mock_data: pd.DataFrame):
    # Check if the function returns two lists and if their size is correct
    df_exceedances = calculate_exceedance_days(mock_data, years)
    best, worst = top3_exceedances(df_exceedances)

    assert isinstance(best, list)
    assert isinstance(worst, list)

    # We have 3 stations in the mocked data, so both lists should have 3 elements each
    assert len(best) == 3
    assert len(worst) == 3


def test_top3_sorting_best_worst(mock_data: pd.DataFrame):
    # Check if the stations are correctly sorted from cleanest to dirtiest
    df_exceedances = calculate_exceedance_days(mock_data, years)
    best, worst = top3_exceedances(df_exceedances)

    # The cleanest should be Gdansk (0 exceedance days)
    assert best[0] == "Gdansk_S1"
    # The worst should be Krakow (3 exceedance days in total)
    assert worst[0] == "Krakow_S1"


def test_nan_behavior():
    # Check if the function handles missing data (NaN) properly
    index = pd.to_datetime(['2015-01-01 10:00:00', '2015-01-01 11:00:00'])
    df_empty = pd.DataFrame({
        "Miejscowość_Kod stacji": index,
        "Pusta_Stacja": [np.nan, np.nan]
    })

    result = calculate_exceedance_days(df_empty, years)
    # The mean of NaN is NaN, which is not > 15, so the result should be 0 or NaN. The sum of NaNs is 0
    assert result.loc[2015, "Pusta_Stacja"] == 0