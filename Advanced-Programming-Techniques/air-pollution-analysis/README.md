# The First Project: Air Pollution - PM2.5 Analysis

The project is a Jupyter Notebook-based analysis pipeline for processing and visualizing PM2.5 air pollution data sourced from the Polish Chief Inspectorate of Environmental Protection (GIOŚ). It covers data acquisition, cleaning, aggregation, and visual analysis across three years — 2014, 2019, and 2024 — with a focus on identifying pollution trends and WHO standard exceedances across Polish monitoring stations.

## My Contribution

I was responsible for Part 3 and Part 4, which involved implementing `prepare_heatmap_data` for reshaping the merged dataset into long format suitable for visualization, and `create_heatmap` for rendering a panel of per-city monthly PM2.5 heatmaps using Matplotlib. In Part 4, I wrote `count_exceedance_days` to calculate the number of days per year exceeding the WHO threshold of 15 µg/m³, `top3_exceedances` to identify the three cleanest and three most polluted stations, and `create_grouped_barplot` to display the results as a grouped bar chart.

## Project Stages

- Downloading and extracting PM2.5 hourly measurement data for 2014, 2019, and 2024 from the GIOŚ archive.
- Downloading station metadata and using it to standardize and update station codes.
- Cleaning, aligning, and merging all yearly datasets into a single Excel file.
- Computing monthly averages and visualizing trends for Warsaw and Katowice.
- Generating a heatmap panel showing monthly PM2.5 averages per city across all three years.
- Counting days exceeding the WHO PM2.5 norm (15 µg/m³) and comparing the best and worst performing stations.

## Installation and Requirements

The project requires Python ≥ 3.8. All dependencies are listed in `requirements.txt`.
Install using the command:

```bash
pip install -r requirements.txt
```

# Running the Notebook

## Execution

Open and run the notebook cell by cell in order:

```bash
jupyter notebook air_pollution_analysis.ipynb
```

All cells must be executed sequentially, as each part builds on the outputs of the previous one. The notebook downloads all required data automatically — no manual file preparation is needed.

## Data Sources

All data is fetched automatically from two GIOŚ endpoints:

- **PM2.5 hourly measurements**: ZIP archives for 2014, 2019, and 2024, downloaded by archive ID from `https://powietrze.gios.gov.pl/pjp/archives/downloadFile/`
- **Station metadata**: A separate Excel file containing station codes, names, and city assignments (archive ID `584`)

# Part Descriptions

## Part 1 — Data Loading and Cleaning

### Input:
- GIOŚ ZIP archives for 2014, 2019, 2024 (fetched by ID)
- Station metadata Excel file

### Output:
- `pomiarPM25_lata_2014_2019_2024.xlsx` — cleaned and merged dataset

### Functions:

**`download_gios_archive(year, gios_id, filename)`**
Downloads a ZIP archive from the GIOŚ API by ID, extracts the target Excel file in memory, and loads it into a DataFrame without saving to disk.

**`download_metadata(gios_id, filename)`**
Downloads the station metadata Excel file directly from the GIOŚ API.

**`standardize_format(df)`**
Standardizes the raw DataFrame: promotes the first row to column headers, parses the datetime index, strips column name whitespace, and converts all values to numeric.

**`update_station_codes(df)`**
Renames station columns from legacy codes to current codes using a mapping derived from the metadata (column 4 → column 1).

**`remove_unique_stations(df, common_codes)`**
Keeps only the columns (station codes) that are present in all three yearly DataFrames, ensuring a consistent set of stations across years.

**`add_multiindex_headers(df, combined_headers)`**
Adds a `MultiIndex` to column headers combining city name and station code.

**`shift_midnight_to_previous_day(df)`**
Shifts midnight timestamps (`00:00:00`) back by one calendar day to correctly assign them to the preceding day.

**`check_equal_station_count(dfs)`**
Sanity check: verifies that all DataFrames have the same number of columns after cleaning. Exits with an error if not.

**`check_correct_day_count(dfs)`**
Sanity check: verifies that each yearly DataFrame contains the correct number of days (365 or 366 for leap years). Exits with an error if not.

**`clean_files(dfs)`**
Orchestrates all cleaning steps: standardizes format, updates station codes, retains only common stations, applies MultiIndex headers, adjusts midnight timestamps, and runs both sanity checks.

**`merge_dataframes(dfs)`**
Concatenates all cleaned yearly DataFrames row-wise, flattens the MultiIndex column headers into `City_StationCode` format, and resets the datetime index for Excel export.

**`save_to_excel(merged_dfs)`**
Saves the final merged DataFrame to `pomiarPM25_lata_2014_2019_2024.xlsx`.

## Part 2 — Monthly Trend Visualization

### Input:
- `pomiarPM25_lata_2014_2019_2024.xlsx`

### Output:
- Line chart comparing monthly average PM2.5 concentrations in Warsaw and Katowice for 2014 vs. 2024

### Logic:

1. Reloads the merged Excel file and resamples to monthly averages.
2. Filters to Warsaw and Katowice columns only, averaging across multiple stations in Warsaw.
3. Plots side-by-side line charts for 2014 and 2024.

**Key findings:** PM2.5 concentrations are highest in Q1 and Q4. Katowice is more polluted than Warsaw. Both cities show a significant improvement over the 10-year period, with the gap between them narrowing by 2024.

## Part 3 — Monthly Heatmap Panel

### Input:
- Output of `merge_dataframes(cleaned_dfs)` — merged DataFrame

### Output:
- Panel of heatmaps, one per city, showing monthly average PM2.5 for 2014, 2019, and 2024

### Functions:

**`prepare_heatmap_data(df_input)`**
Reshapes the merged DataFrame into long format with columns `[Year, Month, City, PM2.5]`. Resamples to monthly averages, groups by city (averaging across stations in the same city), and melts into the long format required for heatmap rendering.

**`create_heatmap(df_long)`**
Renders a grid of heatmaps (3 columns, as many rows as needed) using Matplotlib's `imshow`. Each subplot shows a 3×12 matrix (years × months) for one city, color-coded using the `RdYlGn_r` colormap (range: 0–60 µg/m³), with values printed inside each cell. A shared colorbar is placed to the right of the grid.

**Key findings:** In 2014 the most polluted cities were Kraków, Legionowo, and Katowice. By 2024, no station recorded monthly averages above 36 µg/m³, reflecting a clear improvement trend across all monitored cities.

## Part 4 — WHO Exceedance Days Analysis

### Input:
- Output of `merge_dataframes(cleaned_dfs)` — merged DataFrame

### Output:
- Grouped bar chart comparing the 3 cleanest and 3 most polluted stations across 2014, 2019, and 2024

### Functions:

**`count_exceedance_days(df_input)`**
Computes daily mean PM2.5 per station, flags days exceeding 15 µg/m³ (the WHO guideline), and sums the flags per year. Returns a DataFrame indexed by year (2014, 2019, 2024) with exceedance day counts per station.

**`top3_exceedances(exceedance_summary)`**
Sums exceedance days across all years per station, then returns the 3 stations with the fewest total exceedances (cleanest) and the 3 with the most (most polluted).

**`create_grouped_barplot(df)`**
Calls `count_exceedance_days` and `top3_exceedances` internally, then plots a grouped bar chart with one bar group per station (6 total), three bars per group (one per year, colored blue/red/green), bar labels, a vertical dividing line between the clean and polluted groups, and group annotations.

**Key findings:** The most polluted stations recorded roughly 150 more exceedance days than the cleanest ones. In 5 out of 6 highlighted stations, the number of days exceeding WHO norms declined over the 2014–2024 period.
