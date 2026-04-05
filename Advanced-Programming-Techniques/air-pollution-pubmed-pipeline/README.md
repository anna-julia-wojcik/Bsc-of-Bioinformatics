# The Final Project: Air Pollution - Pubmed Pipeline

The project is an automated data processing pipeline managed by the Snakemake tool.
It integrates environmental data analysis (PM2.5 concentrations from GIOŚ) with bibliometric analysis of medical literature (PubMed) in order to examine the correlation between air quality and trends in scientific publications in the years defined in the configuration (e.g., 2019, 2024).

## Project Stages

- Workflow automation using Snakemake.
- Downloading and cleaning PM2.5 content data (using modules from Project 3).
- Downloading scientific publication metadata from the PubMed database using the Entrez API.
- Generating an automatic final report in Markdown format.

## Installation and Requirements

The project requires Python ≥ 3.8. All dependencies are listed in `requirements.txt`.
Install using the command:

```bash
pip install -r requirements.txt
```

# Running the Pipeline

## Configuration

The pipeline is configured through the `config.yaml` file.

The user should replace `your_email@gmail.com` with their own email address.

The user may freely modify:

- the year range (`years`)
- the list of cities (`cities`)
- PubMed query parameters (`query`, `email`, `max_results`)

Example configuration file:

```yaml
years: [2019, 2024]
cities: ["Warszawa", "Katowice"]

pubmed:
  query: "PM2.5 Poland"
  email: "a.wojcik55@student.uw.edu.pl"
  max_results: 20
```

You can specify different years (e.g., `[2018, 2020]`), different cities, or change the PubMed query.

## Running the Pipeline

The pipeline is launched with the command:

```bash
snakemake -s Snakefile_task4 --cores 1
```

The `--cores` parameter specifies the number of CPU cores used for computation (can be increased if resources are available).

## Bonus

During the project, a change in the argument specification of newer versions of Snakemake was identified.

Attempting to explicitly force checksum-only verification using the command:

```bash
snakemake -s Snakefile_task4 --cores 1 --rerun-triggers checksum
```

will result in an argument validation error (`invalid choice`). In the current version of the software, the `checksum` mechanism is no longer a standalone configuration option — it has become an integral part of the internal verification logic (implemented within the `mtime` or `input` mode).

According to the Snakemake technical documentation:

> **--rerun-triggers**
> Possible choices: code, input, mtime, params, software-env
> Define what triggers the rerunning of a job. By default, all triggers are used, which guarantees that results are consistent with the workflow code and configuration. If you rather prefer the traditional way of just considering file modification dates, use **--rerun-trigger mtime**.

As a result, the project's run instructions recommend using the `mtime` flag or default settings. This approach ensures correct data consistency verification (including file metadata checks) without generating syntax errors.

# Run Scenarios

## Scenario 1

The user sets the following in `config.yaml`:

```yaml
years: [2021, 2024]
```

Then runs:

```bash
snakemake -s Snakefile_task4 --cores 1
```

The pipeline performs full processing for both years:
- calculates PM2.5 for 2021 and 2024,
- retrieves and analyzes PubMed data for 2021 and 2024,
- generates a report covering the years {2021, 2024}.

Correctness is verified based on Snakemake logs (rules visibly executed for both years) and the presence of generated output files and the report for {2021, 2024}.

## Scenario 2 (Incremental Execution)

The user changes the configuration to:

```yaml
years: [2019, 2024]
```

and runs again:

```bash
snakemake -s Snakefile_task4 --cores 1
```

The pipeline performs only the missing steps:
- calculates PM2.5 for 2019 (2024 is skipped),
- retrieves and analyzes PubMed data for 2019 (2024 is skipped),
- generates a new report for {2019, 2024}.

Verification is based on Snakemake logs (no re-execution of rules for 2024; visible in job IDs showing fewer tasks since files for 2024 are not recreated).

# Module Descriptions

## 1. Snakefile_task4

### Input:
- configuration file `config/task4.yaml`
- years defined in `config["years"]`
- PubMed query parameters from the `pubmed` section

### Output:
- PM2.5 result files in `results/pm25/{year}/`
- PubMed result files in `results/literature/{year}/`
- final report `results/report/report_task4.md`

### Logic:

`Snakefile_task4` defines the workflow in Snakemake and manages dependencies between analysis stages.

For each year from the configuration:
1. runs PM2.5 data analysis,
2. runs literature retrieval and analysis from PubMed,
3. after all analyses are complete, generates the final report.

The `all` rule designates the report as the pipeline's final target. The Snakefile operates incrementally.

## 2. pubmed_fetch.py

### Input:
- configuration file `config/task4.yaml`
- year passed by Snakemake (`{year}`)
- parameters from the `pubmed` section:
  - `query`
  - `email`
  - `max_results`

### Output:
- `results/literature/{year}/pubmed_papers.csv`
- `results/literature/{year}/summary_by_year.csv`
- `results/literature/{year}/top_journals.csv`

### Logic:

The module retrieves and analyzes articles from PubMed for the specified year.

1. Reads the configuration and builds a query in the form: `(query) AND {year}[pdat]`.
2. Sends the query to PubMed (ESearch), then retrieves full article records (EFetch).
3. Extracts from each record:
   - PMID,
   - title,
   - publication year,
   - journal name,
   - authors.
4. Sorts data to ensure result determinism.
5. Saves:
   - the full article list to `pubmed_papers.csv`,
   - the article count per year to `summary_by_year.csv`,
   - the 10 most frequently occurring journals to `top_journals.csv`.

The script is run by Snakemake separately for each year defined in the configuration file.

## 3. air_pollution_main.py

### Input:
- configuration file `config/task4.yaml`
- year passed by Snakemake (`{year}`)
- archival PM2.5 data from GIOŚ for the specified year
- measurement station metadata
- list of cities from the `cities` section in the configuration

### Output:
- `results/pm25/{year}/daily_means.csv`
- `results/pm25/{year}/exceedance_days.csv`

### Logic:

The module is responsible for downloading, cleaning, and analyzing PM2.5 data for the selected year.

1. Loads the configuration and prepares URLs for downloading archival GIOŚ data.
2. Downloads hourly PM2.5 data and station metadata.
3. Cleans and merges the data, then filters it to the cities specified in the configuration.
4. Calculates:
   - daily mean PM2.5 concentrations,
   - number of days exceeding the standard.
5. Saves results to CSV files in the `results/pm25/{year}/` directory.

The script is run by Snakemake separately for each year defined in the configuration file.

## 4. create_report.py

### Input:
- configuration file `config/task4.yaml`
- PM2.5 result files:
  - `results/pm25/{year}/exceedance_days.csv`
- PubMed result files:
  - `results/literature/{year}/pubmed_papers.csv`
  - `results/literature/{year}/summary_by_year.csv`

### Output:
- final report in Markdown format: `results/report/raport_task4.md`

### Logic:

The module generates the final report combining PM2.5 analysis results and PubMed literature.

1. Reads the configuration and determines the years for analysis.
2. Combines PM2.5 exceedance data from individual years and inserts it into the report.
3. For each year, analyzes PubMed files, summarizes the article count, and selects a few sample publications.
4. Creates report sections covering:
   - days with PM2.5 exceedances,
   - a PubMed literature review with publication trends.
5. Saves the report to the specified Markdown file.

The script is called by Snakemake once, after all PM2.5 and PubMed analyses for the specified years are complete.

## 5. test_pubmed_fetch.py

### Input:
- the `extract_year` function from the `pubmed_fetch.py` module
- sample date values in various formats:
  - full date: `"2024 May 12"`
  - year only: `"2019"`
  - invalid values: `"Brak"`, `None`

### Output:
- result of the `extract_year` function as a string representing the publication year

### Logic:

The test module verifies the correctness of the function that parses the year from a PubMed record.

Tests cover:
1. Correctly extracting the year from a full date.
2. Extracting the year when only the year number is provided.
3. Returning the default year from the configuration for invalid or missing date data.
4. Verifying output type consistency (always a string).

The test is run with the command:

```bash
python -m pytest tests/test_pubmed_fetch.py
```