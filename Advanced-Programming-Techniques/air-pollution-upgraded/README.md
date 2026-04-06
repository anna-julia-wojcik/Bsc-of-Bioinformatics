# The Third Project: Air Pollution - PM2.5 Analysis (Modular Version)

The project is a modular Python pipeline for processing and visualizing PM2.5 air pollution data sourced from the Polish Chief Inspectorate of Environmental Protection (GIOŚ). It builds on the previous project by refactoring the code into separate `.py` modules, extending the analysis to years 2015, 2018, 2021, and 2024, and adding a comprehensive pytest test suite. The main analysis is orchestrated from a Jupyter Notebook (`air_pollution_analysis.ipynb`) that imports from the dedicated modules.

## Task description and requirements
[Task description (polish)](https://github.com/anna-julia-wojcik/Bsc-of-Bioinformatics/blob/main/Advanced-Programming-Techniques/air-pollution-upgraded/task_requirements.txt)

## My Contribution

My specific responsibility covered the visualization and exceedance analysis modules. I implemented `heatmap.py` in full — `prepare_heatmap_data` for reshaping the merged dataset into long format and `create_heatmap` for rendering the per-city monthly PM2.5 heatmap panel. I also implemented `grouped_barplot.py`, including `calculate_daily_means`, `calculate_exceedance_days`, `top3_exceedances`, `create_grouped_barplot`, `calculate_voivodeship_exceedances`, and `create_voivodeship_exceedances_barplot` (Task 5 — the voivodeship-level extension). I wrote the corresponding test files `test_heatmap.py` and `test_grouped_barplot.py`.

## Project Stages

- Downloading PM2.5 hourly measurement archives for 2015, 2018, 2021, and 2024 from the GIOŚ API.
- Fetching station metadata to standardize legacy codes and assign geographic locations to the data.
- Cleaning, filtering, and merging the yearly datasets into a single, unified Excel file.
- Computing monthly averages and plotting line charts to compare PM2.5 trends across selected cities.
- Generating a panel of heatmaps to visualize monthly PM2.5 levels for each city across all analyzed years.
- Counting exceedance days over the 15 µg/m³ threshold and creating bar charts to compare the best/worst stations and voivodeship averages.

## Installation and Requirements

The project requires Python ≥ 3.10 (due to modern type hinting syntax). Install all dependencies with:

```bash
pip install -r requirements.txt
```

# Running the Project

## Notebook

Open and run the notebook cell by cell in order:

```bash
jupyter notebook air_pollution_analysis.ipynb
```

All cells must be executed sequentially, as each part depends on the outputs of the previous one. All data is downloaded automatically — no manual file preparation is needed.

## Tests

Run the full test suite with:

```bash
pytest
```

Or run tests for a specific module:

```bash
pytest test_data_preprocessing.py
pytest test_station_yearly_means.py
pytest test_heatmap.py
pytest test_grouped_barplot.py
```

## Data Sources

All data is fetched automatically from two GIOŚ endpoints:

- **PM2.5 hourly measurements**: ZIP archives for 2015, 2018, 2021, and 2024, downloaded by archive ID from `https://powietrze.gios.gov.pl/pjp/archives/downloadFile/`
- **Station metadata**: A separate Excel file containing current and legacy station codes, city and voivodeship assignments

# Module Descriptions

## `data_preprocessing.py` — Data Loading and Cleaning

### Input:
- GIOŚ ZIP archives for the configured years (fetched by archive ID)
- Station metadata Excel file

### Output:
- A merged DataFrame saved as `pomiarPM25_lata_<years>.xlsx`

### Functions:

**`download_gios_archive(year, gios_id, gios_archive_url, filename)`**
Downloads a ZIP archive from the GIOŚ API by ID, extracts the target Excel file in memory, and returns it as a DataFrame.

**`download_metadata(gios_id, gios_archive_url, filename)`**
Downloads the station metadata Excel file directly from the GIOŚ API, with proper header parsing.

**`remove_rows(df)`**
Filters the raw DataFrame to keep only rows containing datetime values or the `"Kod stacji"` header row, removing any extraneous metadata rows.

**`unify_format(df)`**
Promotes the first row to column headers, parses the datetime index (floored to the minute), strips column name whitespace, and converts all values to numeric.

**`update_code(df, met)`**
Renames station columns from legacy codes to current ones using the metadata. Handles stations with multiple comma-separated old codes.

**`remove_unique(df, common_codes)`**
Retains only columns whose station codes appear across all yearly DataFrames.

**`merge_headers(df, merged_headers)`**
Applies a `MultiIndex` to column headers, combining city name (`Miejscowosc`) and station code (`Kod stacji`).

**`previous_day(df)`**
Shifts midnight timestamps (`00:00:00`) back by one calendar day to correctly attribute them to the preceding day.

**`check_equal_station_count(dfs)`**
Sanity check: verifies that all DataFrames in the dict have the same number of columns. Exits with an error if not.

**`check_correct_days_count(dfs)`**
Sanity check: verifies that each yearly DataFrame contains the correct number of calendar days (365 or 366 for leap years). Exits with an error if not.

**`clean_files(dfs, met)`**
Orchestrates all cleaning steps in order: row removal, format standardization, code updates, common station filtering, MultiIndex headers, midnight timestamp correction, and both sanity checks.

**`merge_dfs(dfs)`**
Concatenates all cleaned yearly DataFrames row-wise, flattens the MultiIndex headers into `City_StationCode` format, and resets the datetime index.

**`save_to_excel(merged_dfs, years)`**
Saves the final merged DataFrame to `pomiarPM25_lata_<years>.xlsx`.

---

## `station_yearly_means.py` — Monthly Averages and Line Chart

### Input:
- Merged DataFrame from `merge_dfs`

### Output:
- Line chart comparing monthly average PM2.5 concentrations across selected cities and years

### Functions:

**`calculate_monthly_means(df, years, is_city)`**
Resamples the DataFrame to monthly averages. If `is_city=True`, groups by city name (averaging across stations in the same city); if `False`, groups by individual station code. Filters to the specified years and formats the index as a `PeriodIndex`.

**`plot_line_chart(df, cities, years)`**
Draws a multi-line chart for the specified cities and years, using a `tab20` colormap to assign distinct colors to each city–year combination.

**Key findings (2015 vs. 2024):** PM2.5 concentrations are highest in Q1 and Q4. Katowice remains more polluted than Warsaw. Both cities show a significant downward trend over the period, with the gap between them narrowing by 2024.

---

## `heatmap.py` — Monthly Heatmap Panel

### Input:
- Merged DataFrame from `merge_dfs`

### Output:
- Panel of heatmaps, one per city, showing monthly average PM2.5 for 2015, 2018, 2021, and 2024

### Functions:

**`prepare_heatmap_data(df_input)`**
Reshapes the merged DataFrame into long format with columns `[Year, Month, City, PM2.5]`. Resamples to monthly averages, groups by city (averaging across stations in the same city via a transpose–groupby–transpose pattern), and melts into long format.

**`create_heatmap(df_long)`**
Renders a grid of heatmaps (3 columns, as many rows as needed) using Matplotlib's `imshow`. Each subplot shows a years × 12 matrix for one city, color-coded with the `RdYlGn_r` colormap (range: 0–60 µg/m³), with numeric values printed inside each cell. A shared colorbar is placed to the right of the grid.

---

## `grouped_barplot.py` — Exceedance Days Analysis and Bar Charts

### Input:
- Merged DataFrame from `merge_dfs`
- Station metadata (for voivodeship-level analysis)

### Output:
- Grouped bar chart for the 3 cleanest and 3 most polluted stations
- Grouped bar chart of average exceedance days per voivodeship (Task 5)

### Functions:

**`calculate_daily_means(input_df)`**
Resamples the hourly data to daily means by setting the datetime column as index.

**`calculate_exceedance_days(input_df, years)`**
Flags daily averages exceeding 15 µg/m³, then groups by year and sums the flags to produce a per-station exceedance day count for each year.

**`top3_exceedances(exceedances_summary)`**
Sums exceedance days across all years per station and returns the 3 cleanest and 3 most polluted station names.

**`create_grouped_barplot(df, years)`**
Calls `calculate_exceedance_days` and `top3_exceedances` internally, then plots a grouped bar chart with one group per station (6 total), one bar per year per group, a vertical dividing line between the clean and polluted halves, and group annotations. Bar widths and offsets are computed dynamically based on the number of years.

**`calculate_voivodeship_exceedances(input_df, metadata, years)`**
Extends the exceedance analysis to the voivodeship level: maps each station code to its voivodeship via the metadata, computes average exceedance days per voivodeship per year, and returns a pivot table indexed by voivodeship.

**`create_voivodeship_exceedances_barplot(plot_df)`**
Renders a grouped bar chart of average exceedance days per voivodeship, with rotated x-axis labels, bar value annotations, a clean spine style, and a year-labeled legend.

**Key findings:** The most polluted stations recorded roughly 150 more exceedance days than the cleanest ones. In 5 out of 6 highlighted stations, exceedance days declined over the analysis period. At the voivodeship level, Śląskie and Małopolskie consistently report the highest exceedance counts.

---

## Test Suite

Tests are written using `pytest` with `unittest.mock` for isolating external API calls.

**`test_data_preprocessing.py`** covers: `download_gios_archive` (mocked ZIP + Excel), `download_metadata` (mocked response), `remove_rows` (correctness, station code presence, index reset), `unify_format` (header row, station code removal, datetime index, numeric values), `update_code` (correct code replacement), `remove_unique` (column removal), `merge_headers` (MultiIndex application), `previous_day` (midnight shift), `check_equal_station_count` (pass and fail cases), `check_correct_days_count` (regular year, leap year, and fail case), `merge_dfs` (row count, column names, index restoration).

**`test_station_yearly_means.py`** covers: `calculate_monthly_means` — return type and PeriodIndex format, city vs. station column parsing, monthly average calculation correctness, year range filtering, and empty year range handling.

**`test_heatmap.py`** covers: `prepare_heatmap_data` — result type and column names, correct year/month extraction, city grouping and averaging correctness, index column removal, and unique city identification.

**`test_grouped_barplot.py`** covers: `calculate_exceedance_days` — result type and year index, exceedance counting logic per station, NaN handling. `top3_exceedances` — list types and sizes, correct sorting of cleanest and most polluted stations.
