import os
import yaml
import pandas as pd

import data_preprocessing as dpp
import grouped_barplot as gbp


def select_cities(df: pd.DataFrame, config) -> pd.DataFrame:
    """
    Fetches cities provided in the configurations and filters out stations that match the cities in the configurations.

    Args:
        df (pd.DataFrame): data from which specific cities need to be filtered
        config: configurations loaded from the .yaml file
    Returns:
        df (pd.DataFrame): data with specific cities filtered
    """
    # Load settings from the config file
    cities = config.get("cities", ["Warszawa", "Katowice"])
    columns_to_keep = []

    # Name of the date column, which the later function looks for
    date_column = "Miejscowość_Kod stacji"

    for col in df.columns:
        # If it's the date column, we keep it
        if col == date_column:
            columns_to_keep.append(col)
            continue

        # We filter the rest by cities
        for city in cities:
            if city in col:
                columns_to_keep.append(col)
                break

    if columns_to_keep:
        df = df[columns_to_keep]

    return df


def prepare_configuration(config_path, year):
    """
    Loads configuration from the file and prepares data needed for scraping from the gios website.

    Args:
        config_path (str): path to the .yaml configuration file
        year (int): the year being processed
    Returns:
        config: configurations loaded from the .yaml file
        gios_archive_url (str): path to the website for downloading data
        gios_url_ids (dict): original ids for each year for downloading data
        gios_pm25_file (dict): original excel file names for each year for downloading data
    """
    # Load settings from the config file
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
    gios_url_ids = {2015: '236', 2018: '603', 2019: '322', 2021: '486', 2024: '582'}
    gios_pm25_file = {2015: '2015_PM25_1g.xlsx', 2018: '2018_PM25_1g.xlsx', 2019: '2019_PM25_1g.xlsx',
                      2021: '2021_PM25_1g.xlsx', 2024: '2024_PM25_1g.xlsx'}

    if year not in gios_url_ids:
        raise ValueError(f"No data for year {year}")

    return config, gios_archive_url, gios_url_ids, gios_pm25_file


def download_and_clean_data(year, config, gios_archive_url, gios_url_ids, gios_pm25_file) -> pd.DataFrame:
    """
    Scrapes data from the gios website, cleans and merges files, and filters data for specific cities.

    Args:
        year (int): the year being processed
        config: configurations loaded from the .yaml file
        gios_archive_url (str): path to the website for downloading data
        gios_url_ids (dict): original ids for each year for downloading data
        gios_pm25_file (dict): original excel file names for each year for downloading data
    Returns:
        city_dfs (pd.DataFrame): cleaned data filtered only for the specific year and cities
    """
    # Downloading and cleaning data (for a single year)
    data_for_year = {year: dpp.download_gios_archive(year, gios_url_ids[year], gios_archive_url, gios_pm25_file[year])}
    metadata = dpp.download_metadata('622', gios_archive_url, 'Metadane oraz kody stacji i stanowisk pomiarowych.xlsx')

    # Note: Assumes functions inside 'wczytywanie_i_czyszczenie_danych' were also renamed to English
    processed_dfs = dpp.clean_files(data_for_year, metadata)
    merged_dfs = dpp.merge_dfs(processed_dfs)
    city_dfs = select_cities(merged_dfs, config)

    return city_dfs


def calculate_and_save_results(city_dfs, year, output_exceedances_csv, output_daily_csv):
    """
    Calls functions that calculate the number of days exceeding the PM2.5 norm and daily means, then saves them to files.

    Args:
        city_dfs (pd.DataFrame): cleaned data filtered only for the specific year and cities
        year (int): the year being processed
        output_exceedances_csv (str): path to the file where exceedance data will be saved
        output_daily_csv (str): path to the file where daily means data will be saved
    Returns:
    """
    # Ensure the output folder exists
    os.makedirs(os.path.dirname(output_exceedances_csv), exist_ok=True)

    # Calculate daily means
    df_daily = gbp.calculate_daily_means(city_dfs)
    df_daily.reset_index(names=["Date"]).to_csv(output_daily_csv, sep=';', decimal=',', header=True, index=False,
                                                encoding="utf-8")

    # Calculate days exceeding the norm
    df_exceedances = gbp.calculate_exceedance_days(df_daily, [year])
    df_exceedances.reset_index(names=["Year"]).to_csv(output_exceedances_csv, sep=';', decimal=',', header=True, index=False, encoding="utf-8")


def analyze_selected_year(year, config_path, output_exceedances_csv, output_daily_csv):
    """
    This function ties the other functions in the file together. Loads, cleans, filters, and saves the data.

    Args:
        year (int): the year being processed
        config_path (str): path to the .yaml configuration file
        output_exceedances_csv (str): path to the file where exceedance data will be saved
        output_daily_csv (str): path to the file where daily means data will be saved
    Returns:
    """
    # Configuration
    config, gios_archive_url, gios_url_ids, gios_pm25_file = prepare_configuration(config_path, year)

    # Download, clean, and save the data
    city_dfs = download_and_clean_data(year, config, gios_archive_url, gios_url_ids, gios_pm25_file)
    calculate_and_save_results(city_dfs, year, output_exceedances_csv, output_daily_csv)


if 'snakemake' in globals():
    # Check if the script was run by snakemake and call the main function
    analyze_selected_year(
        year=int(snakemake.wildcards.year),
        config_path=snakemake.params.conf_path,
        output_exceedances_csv=snakemake.output.exc,
        output_daily_csv=snakemake.output.daily
    )