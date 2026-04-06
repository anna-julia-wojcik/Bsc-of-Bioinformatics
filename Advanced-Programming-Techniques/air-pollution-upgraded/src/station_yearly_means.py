import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#--------------------------------------------------------------------------------------------

def calculate_monthly_means(df: pd.DataFrame, years: list[int], is_city: bool) -> pd.DataFrame:
    """
    Calculates the monthly average PM2.5 concentration in various locations (cities/stations).

    :param df: DataFrame containing measurement data
    :param years: List of years for which we want the measurements
    :param is_city: If True, calculates the average for cities; if False, for stations
    :return: DataFrame with averaged measurement data
    """
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # Determine whether to extract data for specific stations or cities
    if is_city:
        df.columns = [col.split('_')[0] for col in df.columns]
    else:
        df.columns = [col.split('_')[-1] for col in df.columns]

    # Average by month
    df = df.resample('ME').mean()

    # Average columns from the same locations (useful when grouping by cities)
    df = df.T.groupby(level=0).mean().T

    # Filter by selected years and format the index
    df = df[df.index.year.isin(years)]
    df.index = df.index.to_period('M')

    return df

#--------------------------------------------------------------------------------------------

def plot_line_chart(df: pd.DataFrame, cities: list[str], years: list[int]) -> None:
    """
    Draws a line chart displaying the average PM2.5 air pollution in specified cities and years.

    :param df: DataFrame containing measurement data from various cities and years
    :param cities: List of cities to be visualized on the chart
    :param years: List of years to be plotted
    """
    df = df.copy()
    df = calculate_monthly_means(df, years, True)

    # Create a list of colors for the chart lines
    num_lines = len(cities) * len(years)
    cmap = plt.get_cmap('tab20', num_lines)
    colors = cmap(np.arange(num_lines))

    plt.figure(figsize=(12, 6))
    months = [i for i in range(1, 13)]

    color_index = 0
    for city in cities:
        for year in years:
            plt.plot(months, df[city][df.index.year == year], 'o-', linewidth=2, markersize=5, color=colors[color_index], label=f'{city} in {year}')
            color_index += 1

    plt.xlabel('Month', size=12)
    plt.ylabel('Average PM2.5 concentration', size=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(months)
    plt.title(f'Monthly average PM2.5 concentration in years {years}', size=15, weight='bold')
    plt.legend()
    plt.show()