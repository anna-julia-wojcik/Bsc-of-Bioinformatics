import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_daily_means(input_df: pd.DataFrame) -> pd.DataFrame:
    df = input_df.copy()

    # Instead of the previous approach with creating new columns, first extract date information from 'index', then remove it from df
    df.index = pd.to_datetime(df.pop('Miejscowość_Kod stacji'))
    df = df.resample('D').mean()

    return df


def calculate_exceedance_days(input_df: pd.DataFrame, years: list) -> pd.DataFrame:
    """
    Calculates the number of days in specific years where the average daily PM2.5 concentration exceeded 15 µg/m³.

    Args:
        input_df (pd.DataFrame): DataFrame with hourly PM2.5 concentration data
        years (list): List of years to consider
    Returns:
        pd.DataFrame: Table indexed by years, containing the number of exceedance days for each station
    """
    df = input_df.copy()

    # If the norm is exceeded, mark it as 1. Then group by years and sum (this boils down to summing the ones).
    mark_exceedance = df > 15

    # Group by year extracted from the index (summing immediately as sum() instead of an additional line)
    result = mark_exceedance.groupby(mark_exceedance.index.year).sum()

    #final_result = result.reindex(years)

    return result


def top3_exceedances(exceedances_summary: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Determines the 3 stations with the lowest and 3 with the highest total number of days exceeding the norm.

    Args:
        exceedances_summary (pd.DataFrame): Table indexed by years, containing the number of exceedance days for each station
    Returns:
        tuple[list[str], list[str]]: Tuple containing two lists: first with the names of the 3 cleanest stations, second with the most polluted ones
    """
    # Sort the sum of exceedance days for each station from lowest to highest
    sorted_results = exceedances_summary.sum().sort_values()

    best_results = sorted_results.head(3) # cleanest
    worst_results = sorted_results.tail(3).iloc[::-1] # most polluted

    best_list = [station for station in best_results.index]
    worst_list = [station for station in worst_results.index]

    return best_list, worst_list


def create_grouped_barplot(df: pd.DataFrame, years: list) -> None:
    """
    Displays a grouped bar plot for the 3 stations with the lowest and 3 with the highest number of days exceeding the WHO norm.

    Args:
        df (pd.DataFrame): DataFrame with hourly PM2.5 concentration data (input data for calculations)
        years (list): List of years to consider
    Returns:
        None: The function does not return a value, it only displays the generated plot
    """
    results_df = calculate_exceedance_days(df, years)
    best_stations, worst_stations = top3_exceedances(results_df)

    # Take data only for these six stations
    plot_df = results_df[best_stations + worst_stations].copy()

    # Axis and data configuration
    # Display both city names and station codes
    stations = [f"{col.split('_')[0]},\n{col.split('_')[1]}" for col in plot_df.columns]
    x = np.arange(len(stations)) # placement on the x-axis
    width = 0.8 / len(years)
    offsets = np.linspace(-0.4 + width / 2, 0.4 - width / 2, len(years))
    colors = plt.cm.get_cmap('tab10', len(years)).colors

    # Drawing the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, year in enumerate(years):
        # Draw bars and add numbers above them
        rects = ax.bar(x + offsets[i], plot_df.loc[year].values, width, label=str(year), color=colors[i], edgecolor='black')
        ax.bar_label(rects, fontsize=9)

    # Add axis labels, titles, a line separating the two parts of the plot, and labels for each group of stations
    ax.set_ylabel('Number of exceedance days (>15 µg/m³)', fontsize=12)
    ax.set_title('Comparison of smog days in the 3 cleanest and 3 most polluted stations', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(stations, fontsize=10)
    ax.axvline(x=2.5, color='gray', linestyle='--', linewidth=1)
    ax.text(1, ax.get_ylim()[1]*0.95, "Cleanest", ha='center', color='green')
    ax.text(4, ax.get_ylim()[1]*0.95, "Most Polluted", ha='center', color='red')
    ax.legend(title='Year')

    plt.tight_layout()
    plt.show()


# create_grouped_barplot(merge_dfs(processed_dfs))


def calculate_voivodeship_exceedances(input_df, metadata, years):
    # Voivodeship mapping
    stations_voivodeships = metadata[["Kod stacji", "Województwo"]].dropna().copy()
    stations_voivodeships.drop_duplicates(inplace=True)
    stations_voivodeships["Kod stacji"] = stations_voivodeships["Kod stacji"].str.strip() # remove spaces

    # copy
    df = input_df.copy()

    # Set date as index
    date_column = df.columns[0]
    df[date_column] = pd.to_datetime(df[date_column]) # convert to datetime
    df.set_index(date_column, inplace=True)

    # Filtering
    df = df.select_dtypes(include=['number'])

    # Calculations - borrowed code
    daily_df = df.resample('D').mean()
    exceedances = (daily_df > 15).astype(int)
    stations_result = exceedances.groupby(exceedances.index.year).sum()

    # Restrict data to given years
    stations_result = stations_result.reindex([int(y) for y in years])

    # Transform to long format
    long_result = stations_result.stack().reset_index()
    long_result.columns = ['Year', 'Kod stacji', 'Days_count']

    # Clean names (extracting "City_") - extract only the station code
    long_result['Kod stacji'] = long_result['Kod stacji'].apply(lambda x: x.split('_')[-1] if '_' in str(x) else x)

    # Join voivodeship column based on station codes
    merged_df = long_result.merge(stations_voivodeships, on='Kod stacji')

    # Average number of exceedance days for all stations in a given voivodeship
    final_result = merged_df.groupby(['Województwo', 'Year'])['Days_count'].mean().unstack(level=1)

    return final_result


def create_voivodeship_exceedances_barplot(plot_df):

    # Create bar plot
    ax = plot_df.plot(kind='bar', figsize=(16, 8), width=0.8, color=['#2d6a4f', '#74c69d', '#b7e4c7', '#d8f3dc'])

    # Add titles
    plt.title('Number of days exceeding PM2.5 norm across voivodeships', fontsize=16, pad=20)
    plt.ylabel('Average number of exceedance days', fontsize=12)
    plt.xlabel('Voivodeship', fontsize=12)

    # Add values above bars
    for p in ax.patches:
        if p.get_height() > 0: # get bar height
            ax.annotate(f'{p.get_height():.0f}', # insert text
                        (p.get_x() + p.get_width() / 2., p.get_height()), # text coordinates
                        ha='center',
                        xytext=(0, 9), # text offset relative to the end of the bar
                        textcoords='offset points', # typographic units
                        fontsize=8, rotation=90) # font size; rotate text by 90 degrees

    # Style axes and legend
    plt.legend(title='Measurement Year', bbox_to_anchor=(1, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='-', alpha=0.3)

    # Remove top and right spines for better readability
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.show()