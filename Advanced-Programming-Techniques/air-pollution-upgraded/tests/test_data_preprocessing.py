import sys
import os
import pandas as pd
import datetime
import numpy as np
import pytest
from unittest.mock import MagicMock, patch, Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_preprocessing import download_gios_archive, download_metadata, remove_rows, unify_format, update_code, remove_unique, merge_headers, previous_day, check_equal_station_count, check_correct_days_count, merge_dfs

#-------------------------------------------data-import-tests---------------------------------------

@pytest.fixture
def mock_measurement_df():
    data = {
            0: [
            "Kod stacji",
            "Wskaźnik",
            "Czas uśredniania",
            pd.to_datetime("1/1/2014 1:00"),
            pd.to_datetime("1/1/2014 2:00"),
            pd.to_datetime("1/1/2014 3:00"),
        ],
        1: [
            "DsWrocWisA",
            "PM2.5",
            "1g",
            np.nan,
            np.nan,
            129,
        ],
        2: [
            "KpBydJezdzie",
            "PM2.5",
            "1g",
            104,
            104,
            91,
        ],
        3: [
            "DsBialka",
            "PM2.5",
            "1g",
            63,
            36,
            31,
        ],
    }

    df = pd.DataFrame(data)
    return df

# Tests if download_gios_archive correctly downloads the file from ZIP archives and returns a proper df
def test_download_gios_archive(mock_measurement_df):
    ## Create mock values occurring in the original function
    mock_response = Mock()
    mock_response.content = b'fake zip bytes'
    mock_response.raise_for_status = Mock()


    mock_file = MagicMock()
    mock_zip = MagicMock()
    mock_zip.__enter__.return_value = mock_zip
    mock_zip.open.return_value.__enter__.return_value = mock_file

    ## Replace the behavior of functions from external packages
    with patch("requests.get", return_value=mock_response), \
        patch("zipfile.ZipFile", return_value=mock_zip), \
        patch("pandas.read_excel", return_value=mock_measurement_df):

        ## Call the original function with mock values
        df = download_gios_archive(
            year=2014,
            gios_id="111",
            gios_archive_url="https://fake-url/",
            filename="fake_dane_2014.xlsx"
        )

    assert isinstance(df, pd.DataFrame)
    assert df.equals(mock_measurement_df)

@pytest.fixture
def mock_metadata():
    data = ({
        "Nr": [1, 2, 3, 4],
        "Kod stacji": ["DsWrocAlWisn", "KpBydJezdzie", "DsBogatFrancMOB", "DsBialka"],
        "Stary Kod stacji \n(o ile inny od aktualnego)": ["DsWrocWisA, InnyKod", "", "DsBogatMob", np.nan],
        "Miejscowość": ["Wrocław", "Bydgoszcz", "Bogatynia", "Białka"],
    })
    df = pd.DataFrame(data)

    return df

def test_download_metadata(mock_metadata):
    ## Create mock values occurring in the original function
    mock_response = Mock()
    mock_response.content = b'fake zip bytes'
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response), \
        patch("pandas.read_excel", return_value=mock_metadata):

        df = download_metadata(
            gios_id="123",
            gios_archive_url="https://fake-url/",
            filename="fake_metadane.xlsx"
        )

    assert isinstance(df, pd.DataFrame)
    assert df.equals(mock_metadata)

#-------------------------------------------remove_rows-tests---------------------------------------

# Checks if incorrect rows were properly removed
def test_removal_correctness(mock_measurement_df):
    result = remove_rows(mock_measurement_df)

    col = result.iloc[:, 0]
    assert all(
        isinstance(x, datetime.datetime) or x == "Kod stacji"
        for x in col
    )

# Checks if the row titled "Kod stacji" exists
def test_station_code_exists(mock_measurement_df):
    result = remove_rows(mock_measurement_df)

    assert "Kod stacji" in result.iloc[:, 0].values

# Checks if the index was correctly reset
def test_reset_index_remove_rows(mock_measurement_df):
    result = remove_rows(mock_measurement_df)

    assert list(result.index) == list(range(len(result)))

#-------------------------------------------unify_format-tests---------------------------------------

@pytest.fixture
def mock_for_unify_format():
    data = {
        0: [
            "Kod stacji",
            pd.to_datetime("1/1/2014 1:00"),
            pd.to_datetime("1/1/2014 2:00"),
            pd.to_datetime("1/1/2014 3:00"),
        ],
        1: [
            "DsWrocWisA",
            np.nan,
            np.nan,
            129,
        ],
        2: [
            "KpBydJezdzie",
            104,
            104,
            91,
        ],
        3: [
            "DsBialka",
            63,
            36,
            31,
        ],
    }

    df = pd.DataFrame(data)

    return df

# Checks if the first row is the header
def test_correct_header_row(mock_for_unify_format):
    result = unify_format(mock_for_unify_format)
    column_titles = ["DsWrocWisA", "KpBydJezdzie", "DsBialka"]

    assert list(result.columns) == column_titles

# Checks if the row with station codes was properly removed from the data
def test_station_code_not_in_data(mock_for_unify_format):
    result = unify_format(mock_for_unify_format)

    assert "Kod stacji" not in result.index.astype(str)

# Checks if the index was correctly reset
def test_reset_index_unify_format(mock_for_unify_format):
    result = unify_format(mock_for_unify_format)

    assert result.index.is_monotonic_increasing
    assert result.index.dtype == "datetime64[ns]"

# Checks if the column with dates was set as index and removed from the data
def test_correct_date_index(mock_for_unify_format):
    result = unify_format(mock_for_unify_format)

    assert isinstance(result.index, pd.DatetimeIndex)
    assert result.index.name not in result.columns

# Checks if all column names are strings
def test_column_names_are_strings(mock_for_unify_format):
    result = unify_format(mock_for_unify_format)

    assert all(isinstance(col_name, str) for col_name in result.columns)


# Checks if all values in df are numeric values (or nan)
def test_are_values_numeric(mock_for_unify_format):
    result = unify_format(mock_for_unify_format)

    assert all(pd.api.types.is_numeric_dtype(result[col]) for col in result.columns)

#-------------------------------------------update_code-tests---------------------------------------

@pytest.fixture
def mock_for_update_code():
    data = {
        "Kod stacji": [
            pd.to_datetime("1/1/2014 1:00"),
            pd.to_datetime("1/1/2014 2:00"),
            pd.to_datetime("1/1/2014 3:00"),
        ],
        "DsWrocWisA": [
            np.nan,
            np.nan,
            129,
        ],
        "KpBydJezdzie": [
            104,
            104,
            91,
        ],
        "DsBialka": [
            63,
            36,
            31,
        ],
    }

    df = pd.DataFrame(data)
    df = df.set_index('Kod stacji')
    return df

# Checks if the replacement of codes is successful
def test_correct_code_update(mock_for_update_code, mock_metadata):
    result = update_code(mock_for_update_code, mock_metadata)

    assert list(result.columns) == ["DsWrocAlWisn", "KpBydJezdzie", "DsBialka"]

#-------------------------------------------remove_unique-tests---------------------------------------

@pytest.fixture
def mock_for_remove_unique():
    data = {
        "Kod stacji": [
            pd.to_datetime("1/1/2014 1:00"),
            pd.to_datetime("1/1/2014 2:00"),
            pd.to_datetime("1/1/2014 3:00"),
        ],
        "DsWrocAlWisn": [
            np.nan,
            np.nan,
            129,
        ],
        "KpBydJezdzie": [
            104,
            104,
            91,
        ],
        "DsBialka": [
            63,
            36,
            31,
        ],
    }

    df = pd.DataFrame(data)
    df = df.set_index('Kod stacji')
    return df

# Checks if the removal of columns with non-repeating stations was successful
def test_column_removal(mock_for_remove_unique):
    common_list = ["DsWrocAlWisn", "DsBialka"]
    result = remove_unique(mock_for_remove_unique, common_list)

    assert list(result.columns) == common_list

#-------------------------------------------merge_headers-tests---------------------------------------

@pytest.fixture
def mock_for_merge_headers():
    data = {
        "Kod stacji": [
            pd.to_datetime("1/1/2014 1:00"),
            pd.to_datetime("1/1/2014 2:00"),
            pd.to_datetime("1/1/2014 3:00"),
        ],
        "DsWrocAlWisn": [
            np.nan,
            np.nan,
            129,
        ],
        "DsBialka": [
            63,
            36,
            31,
        ],
    }

    df = pd.DataFrame(data)
    df = df.set_index('Kod stacji')
    return df

# Checks if the column names update was successful
def test_header_merging(mock_for_merge_headers):
    mock_multi_index = [('Wrocław', 'DsWrocAlWisn'), ('Białka', 'DsBialka')]
    result = merge_headers(mock_for_merge_headers, mock_multi_index)

    assert list(result.columns) == mock_multi_index

#-------------------------------------------previous_day-tests---------------------------------------

@pytest.fixture
def mock_for_previous_day():
    data = {
        ("Miejscowość", "Kod stacji"): [
            pd.to_datetime("15/3/2014 0:00", dayfirst=True),
            pd.to_datetime("31/12/2014 23:00", dayfirst=True),
            pd.to_datetime("1/1/2015 00:00", dayfirst=True),
        ],
        ("Wrocław", "DsWrocAlWisn"): [
            np.nan,
            np.nan,
            129,
        ],
        ("Białka", "DsBialka"): [
            63,
            36,
            31,
        ],
    }

    df = pd.DataFrame(data)
    df = df.set_index(('Miejscowość', 'Kod stacji'))
    df.columns = pd.MultiIndex.from_tuples(df.columns)

    return df

# Checks if the date modification works
def test_date_change(mock_for_previous_day):
    result = previous_day(mock_for_previous_day)

    expected_dates = pd.to_datetime([
        "2014-03-14 00:00:00",
        "2014-12-31 23:00:00",
        "2014-12-31 00:00:00",
    ])

    assert (result.index == expected_dates).all()

#-------------------------------------------check_equal_station_count-tests---------------------------------------

# Checks if the function DOES NOT raise an exception for correct values
def test_no_exception_station_count():
    mock_dfs ={
        1: pd.DataFrame(columns=["A", "B"]),
        2: pd.DataFrame(columns=["A", "B"]),
    }
    check_equal_station_count(mock_dfs)

# Checks if the program properly terminates when an exception occurs
def test_exception_station_count():
    mock_dfs = {
        1: pd.DataFrame(columns=["A", "B"]),
        2: pd.DataFrame(columns=["A"]),
    }

    with pytest.raises(SystemExit) as exc:
        check_equal_station_count(mock_dfs)

    assert "Error: The number of columns in the files is different" in str(exc.value)

#-------------------------------------------check_correct_days_count-tests---------------------------------------

# Checks if correct values DO NOT raise an exception
def test_no_exception_days_count():
    # 2023 is a non-leap year
    mock_index = pd.date_range("2023-01-01", "2023-12-31", freq="D")
    mock_df = pd.DataFrame(index=mock_index, data={'x': range(len(mock_index))})

    mock_dfs = {1: mock_df}

    check_correct_days_count(mock_dfs)

# Checks if correct values DO NOT raise an exception (for a leap year)
def test_no_exception_days_count_leap_year():
    mock_index = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    mock_df = pd.DataFrame(index=mock_index, data={'x': range(len(mock_index))})

    mock_dfs = {1: mock_df}

    check_correct_days_count(mock_dfs)

# Checks if raising an exception attempts to terminate the program
def test_exception_days_count():
    year = 2023
    mock_index = pd.date_range("2023-01-01", "2023-12-30", freq="D")
    mock_df = pd.DataFrame(index=mock_index, data={'x': range(len(mock_index))})

    mock_dfs = {1: mock_df}

    with pytest.raises(SystemExit) as exc:
        check_correct_days_count(mock_dfs)

    assert f"Error: The number of days in the file {year}_PM2.5_1g.xlsx is incorrect" in str(exc.value)

#-------------------------------------------merge_dfs-tests---------------------------------------

@pytest.fixture
def mock_for_merge_dfs():
    data_1 = {
        ("Miejscowość", "Kod stacji"): [
            pd.to_datetime("1/1/2014 1:00"),
            pd.to_datetime("1/1/2014 2:00"),
            pd.to_datetime("1/1/2014 3:00"),
        ],
        ("Wrocław", "DsWrocAlWisn"): [
            np.nan,
            np.nan,
            129,
        ],
        ("Białka", "DsBialka"): [
            63,
            36,
            31,
        ],
    }
    df_1 = pd.DataFrame(data_1)
    df_1 = df_1.set_index(('Miejscowość', 'Kod stacji'))
    df_1.columns=pd.MultiIndex.from_tuples(list(df_1.columns))

    data_2 = {
        ("Miejscowość", "Kod stacji"): [
            pd.to_datetime("5/6/2020 4:00"),
            pd.to_datetime("5/6/2020 5:00"),
            pd.to_datetime("5/6/2020 6:00"),
        ],
        ("Wrocław", "DsWrocAlWisn"): [
            115,
            np.nan,
            129,
        ],
        ("Białka", "DsBialka"): [
            63,
            np.nan,
            31,
        ],
    }
    df_2 = pd.DataFrame(data_2)
    df_2 = df_2.set_index(('Miejscowość', 'Kod stacji'))
    df_2.columns = pd.MultiIndex.from_tuples(list(df_2.columns))

    dfs = {2014: df_1, 2020: df_2}

    return dfs

# Checks if row merging was successful
def test_merge_correctness(mock_for_merge_dfs):
    result = merge_dfs(mock_for_merge_dfs)

    assert len(result) == 6

# Checks if the MultiIndex was properly flattened
def test_column_names(mock_for_merge_dfs):
    result = merge_dfs(mock_for_merge_dfs)
    expected_col_names = ['Miejscowość_Kod stacji', 'Wrocław_DsWrocAlWisn', 'Białka_DsBialka']
    print(list(result.columns))
    assert list(result.columns) == expected_col_names

# Checks if the index column was correctly restored to values
def test_reset_index_merge_dfs(mock_for_merge_dfs):
    result = merge_dfs(mock_for_merge_dfs)

    assert 'Miejscowość_Kod stacji' in result.columns

# Checks if column names were not added by accident
def test_no_column_name(mock_for_merge_dfs):
    result = merge_dfs(mock_for_merge_dfs)

    assert result.columns.name is None