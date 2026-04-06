import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np

def prepare_heatmap_data(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Processes data from the file to match the task requirements (groups by city, monthly averages).

    Args:
        df_input (pd.DataFrame): Merged input data from 2014, 2019, 2024 regarding PM2.5 pollution
    Returns:
        pd.DataFrame: Data in long format with columns [Year, Month, City, PM2.5], ready for visualization
    """
    df = df_input.copy()

    # Fix the first column - convert to dates, index by date
    df['date'] = pd.to_datetime(df['index'])
    df = df.set_index('date')
    df = df.drop(columns=['index'])

    # Extract city names from columns and group by time, taking the mean (same operations as in Part 2)
    df_monthly = df.resample('ME').mean()
    city_names = [col.split('_')[0] for col in df_monthly.columns]

    # For convenience: transpose, group by city names and compute means, then transpose back
    df_grouped_cities = df_monthly.T.groupby(city_names).mean().T

    # Prepare labels for long format
    df_grouped_cities['Year'] = df_grouped_cities.index.year
    df_grouped_cities['Month'] = df_grouped_cities.index.month

    # Prepare long format with separated columns for the chart
    df_long = df_grouped_cities.melt(id_vars=['Year', 'Month'], var_name='City', value_name='PM2.5')

    return df_long


def create_heatmap(df_long: pd.DataFrame) -> None:
    """
    Draws a heatmap panel in pure Matplotlib based on data prepared by 'prepare_heatmap_data'.

    Args:
        df_long (pd.DataFrame): DataFrame with data formatted for creating the heatmap chart
    Returns:
        None: The function does not return a value, only displays the finished chart
    """
    # Get unique cities (because names in the table are duplicated) and sort alphabetically
    unique_cities = sorted(df_long['City'].unique())

    # Configure the chart grid - divide into smaller cells for subplots
    n_cols = 3
    n_rows = math.ceil(len(unique_cities) / n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows), sharex=True, sharey=True)
    axes = axes.flatten()

    # Visual settings
    cmap = plt.get_cmap("RdYlGn_r")  # Red-Yellow-Green (reversed)
    vmin, vmax = 0, 60  # Color range
    years = [2014, 2019, 2024]

    # Draw the chart
    for i, city in enumerate(unique_cities):
        ax = axes[i]
        city_data = df_long[df_long['City'] == city]

        # Create a pivot matrix: rows = year, columns = month
        pivot_df = city_data.pivot(index='Year', columns='Month', values='PM2.5')

        # Force the table to have exactly 3 years and 12 months
        pivot_df = pivot_df.reindex(index=years, columns=range(1, 13))

        # Convert to numpy matrix (for imshow)
        data_matrix = pivot_df.to_numpy()

        # Draw (imshow)
        im = ax.imshow(data_matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

        # Manually add numbers inside cells
        rows, cols = data_matrix.shape
        for r in range(rows):
            for c in range(cols):
                val = data_matrix[r, c]
                # Only print if the value exists (is not NaN)
                if not np.isnan(val):
                    ax.text(c, r, f"{val:.0f}", ha="center", va="center", color='white', fontsize=9)

        # Axis labels and title
        ax.set_title(city)
        ax.set_yticks(range(len(years)))
        ax.set_yticklabels(years)
        ax.set_ylabel('Year')
        ax.set_xticks(range(12))
        ax.set_xticklabels(range(1, 13))
        ax.set_xlabel('Month')

    # Adjust chart layout - leave a free margin on the right for the colorbar
    plt.tight_layout(rect=[0, 0, 0.9, 1])

    # Add the colorbar in that free space
    cbar_ax = fig.add_axes([0.92, 0.3, 0.02, 0.4])
    fig.colorbar(im, cax=cbar_ax, label='Average PM2.5 concentration [µg/m3]')

    plt.suptitle('Monthly average PM2.5 concentrations in 2014, 2019 and 2024)', fontsize=20, y=1.02)
    plt.show()
