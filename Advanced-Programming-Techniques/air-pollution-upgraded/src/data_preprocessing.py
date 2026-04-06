import pandas as pd
import requests
import zipfile
import io, os
import sys
import datetime

#----------------------------------------------------------------------------------

# Function to download the specified archive
def download_gios_archive(year: int, gios_id: str, gios_archive_url: str, filename: str) -> pd.DataFrame:
    # Download the ZIP archive into memory
    url = f"{gios_archive_url}{gios_id}"
    response = requests.get(url)
    response.raise_for_status()  # If HTTP error, stop
    df = pd.DataFrame()

    # Open zip in memory
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Find the correct PM2.5 file
        if not filename:
            print(f"Error: {filename} not found.")
        else:
            # Load file into pandas
            with z.open(filename) as f:
                try:
                    df = pd.read_excel(f, header=None)
                except Exception as e:
                    print(f"Error loading {year}: {e}")

    return df

#----------------------------------------------------------------------------------

# Download metadata
def download_metadata(gios_id: str, gios_archive_url: str, filename: str) -> pd.DataFrame:
    url = f"{gios_archive_url}{gios_id}"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.DataFrame()

    try:
        z = io.BytesIO(response.content)
        df = pd.read_excel(z, header=0)
    except Exception as e:
        print(f"Error loading {filename}, {e}")

    return df

#----------------------------------------------------------------------------------

## Definitions of file cleaning functions

# Removes unnecessary rows
def remove_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function builds a mask for df, containing only data of datetime.datetime format and the single value "Kod stacji".
    This cleans the df of unnecessary rows.

    :param df: Data frame in which to filter out redundant rows
    :return: Data frame with only air quality data or station codes
    """
    df = df.copy()
    col = df.iloc[:, 0]

    date_mask = col.apply(lambda x: isinstance(x, datetime.datetime))
    code_mask = col == "Kod stacji"
    mask = date_mask | code_mask
    df.drop(df.index[~mask], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

# Uniform format
def unify_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function sets the appropriate rows/columns as index, unifies their format and the format of the values.

    :param df: data frame where formatting changes will be made
    :return: updated data frame
    """
    df = df.copy()
    df.columns = df.iloc[0] # first row is "Kod stacji", set it as header
    df = df.iloc[1:].copy() # remove this row from df values
    df.reset_index(drop=True, inplace=True)

    # Convert all values in the first column to datetime type
    first_col = df.columns[0]
    df[first_col] = pd.to_datetime(df[first_col], errors='coerce')
    df[first_col] = df[first_col].dt.floor("min")

    # Set the first column as index
    df.set_index(first_col, inplace=True)

    # Clean/unify column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
    )

    # convert values to numbers
    df = df.replace(',', '.', regex=True)
    df = df.apply(pd.to_numeric, errors='coerce')

    return df

# Update station codes
def update_code(df: pd.DataFrame, met: pd.DataFrame) -> pd.DataFrame:
    """
    The function replaces obsolete station codes with new ones, according to the metadata information.

    :param df: data frame where the replacement is performed
    :param met: data frame with measurement metadata
    :return: updated data frame
    """
    df = df.copy()
    # Take only rows where the old code is NOT NaN (nor "" in some cases)
    name_map = {}
    for old_combined, new in zip(met.loc[0:, 'Stary Kod stacji \n(o ile inny od aktualnego)'], met.loc[0:, 'Kod stacji']):
        if pd.notna(old_combined) and old_combined != "":
            # Some stations have multiple old codes
            old_codes = [s.strip() for s in old_combined.split(",")]
            for old in old_codes:
                name_map[old] = new

    # SANITY CHECK 3: Check if the map is not completely empty
    if not name_map:
        print("Warning: No old codes found to map (all were empty). Code map is empty.")

    df = df.rename(columns=name_map) # Replace column names according to the station name map

    return df

# Remove unique codes
def remove_unique(df: pd.DataFrame, common_codes: list[str]) -> pd.DataFrame:
    """
    The function returns a data frame without columns marked with a station code that does not appear in all other data frames.

    :param df: data frame where columns are removed
    :param common_codes: list of codes that repeat in every other data frame
    :return: updated data frame
    """
    df = df.copy()

    return df[common_codes]


# Create MultiIndex in headers
def merge_headers(df: pd.DataFrame, merged_headers: list[tuple[str, str]]) -> pd.DataFrame:
    """
    The function creates MultiIndex headers (Miejscowosc, Kod stacji).

    :param df: data frame where MultiIndex will be added
    :param merged_headers: list containing tuples of station Codes and their corresponding cities
    :return: updated data frame
    """
    df = df.copy()
    df.columns = pd.MultiIndex.from_tuples(merged_headers, names=['Miejscowosc', 'Kod stacji'])

    return df


# Change dates with time 00:00:00 to the previous day
def previous_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function finds dates in the index column where the time is 00:00:00 and moves the calendar day back by 1.

    :param df: data frame where changes will be made
    :return: updated data frame
    """
    df = df.copy()
    time_mask = df.index.time == pd.to_datetime('00:00:00').time()
    # Subtract 1 or 0 days from the index column
    df.index = df.index - pd.to_timedelta(time_mask.astype(int), unit='d')

    return df


# Check if files have an equal number of columns
def check_equal_station_count(dfs: dict[int, pd.DataFrame]) -> None:
    """
    The function checks if the cleaning was successful - whether the files have an equal number of columns.
    If there is a mismatch, it stops the program execution.

    :param dfs: dict of data frames to compare
    """
    station_counts = [df.shape[1] for df in dfs.values()]
    are_equal = len(set(station_counts)) == 1
    if not are_equal:
        sys.exit('Error: The number of columns in the files is different')


# Check if files have the correct number of days in the year
def check_correct_days_count(dfs: dict[int, pd.DataFrame]) -> None:
    """
    The function checks if the cleaning was successful - whether each file has the correct number of calendar days.
    If there is a mismatch, it stops the program execution.

    :param dfs: dict of data frames to check
    """
    from calendar import isleap
    for df in dfs.values():
        year = df.index.year[0]
        days_count = df.index.normalize().unique() # all times -> 00:00:00, only unique values
        correct_days_count = 366 if isleap(year) else 365
        if len(days_count) != correct_days_count:
            sys.exit(f"Error: The number of days in the file {year}_PM2.5_1g.xlsx is incorrect")

#----------------------------------------------------------------------------------

# Call cleaning functions
def clean_files(dfs: dict[int, pd.DataFrame], met: pd.DataFrame) -> dict[int, pd.DataFrame]:
    """
    The function calls other functions responsible for modifying each considered data frame.

    :param dfs: dictionary containing data frames as values on which functions will be executed, and their corresponding years as keys
    :param met: data frame with weather metadata
    :return: dictionary of appropriately modified data frames
    """
    # Unify format and update station code names
    for year, df in dfs.items():
        dfs[year] = remove_rows(df)

    for year, df in dfs.items():
        dfs[year] = unify_format(df)

    for year, df in dfs.items():
        dfs[year] = update_code(df, met)

        # Create a set of common station codes
        common_codes = set()
        for year, df in dfs.items():
            if not common_codes:
                common_codes = set(df.columns)
            else:
                common_codes &= set(df.columns)

        station_city = dict(zip(met.loc[:, 'Kod stacji'], met.loc[:, 'Miejscowość']))

        # Filter out stations that are not in the metadata from the list
        common_codes = [code for code in common_codes if code in station_city]

        # Now remove unique station codes (this will also remove the filtered ones above, leaving exactly 95)
        for year, df in dfs.items():
            dfs[year] = remove_unique(df, list(common_codes))

        # Multi-indexing (city | Station code)
        multi_index = [(station_city[code], code) for code in common_codes]

        for year, df in dfs.items():
            dfs[year] = merge_headers(df, multi_index)

    # Change - midnight to the previous day
    for year, df in dfs.items():
        dfs[year] = previous_day(df)

    # Run sanity checks
    check_equal_station_count(dfs)
    check_correct_days_count(dfs)

    return dfs

#----------------------------------------------------------------------------------

# Merging several dfs into one
def merge_dfs(dfs: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """
    The function merges previously prepared data frames and creates an xlsx file from them

    :param dfs: dict of data frames to merge
    :return: one df created from merged component dfs
    """
    # Merge files by rows
    merged_dfs = pd.concat(dfs.values(), axis=0)

    # Multi-indexing was detached => reattach
    merged_dfs.columns = [f'{city}_{station}' for city, station in merged_dfs.columns]
    merged_dfs.columns.name = None

    # Convert dates back to values so they aren't lost during saving
    merged_dfs = merged_dfs.reset_index(names='Miejscowość_Kod stacji')

    return merged_dfs

#----------------------------------------------------------------------------------

# Save to xlsx file
def save_to_excel(merged_dfs: pd.DataFrame, years: list[int]) -> None:
    # save as xlsx file
    merged_dfs.to_excel(f"pomiarPM25_lata_{'_'.join(map(str, years))}.xlsx", index=False)