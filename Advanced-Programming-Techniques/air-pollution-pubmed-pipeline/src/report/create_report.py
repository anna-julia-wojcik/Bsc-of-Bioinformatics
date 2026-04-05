import pandas as pd
import os
import yaml


def load_pm25_exceedances(years):
    """
    Loads data about PM2.5 concentration exceedances for the given years.

    Args:
        years (list): list of years considered when fetching data
    Returns:
        all_pm25 (list): list of DataFrames containing concentration exceedances for the years passed in the argument
    """
    all_pm25 = []

    for year in years:
        path = f"results/pm25/{year}/exceedance_days.csv"
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, sep=';')
                all_pm25.append(df)
            except Exception as e:
                print(f"Failed to load {path}: {e}")

    return all_pm25


def generate_literature_section(years):
    """
    Based on existing files regarding data fetched from pubmed, prepares a markdown report section
    regarding the number of publications found for specific years and 3 sample articles from those years.

    Args:
        years (list): list of years considered when fetching data
    Returns:
        text (str): prepared report text in markdown format
        summaries (list): list of article counts found for specific years
    """
    text = "\n\n## Literature Review (PubMed)\n"
    summaries = []
    counts = {}

    for year in years:
        summary_path = f"results/literature/{year}/summary_by_year.csv"
        articles_path = f"results/literature/{year}/pubmed_papers.csv"

        if os.path.exists(summary_path):
            try:
                summary = pd.read_csv(summary_path)
                summaries.append(summary)

                # Fetch information on how many publications were generally found for a given year
                if not summary.empty:
                    count = summary.iloc[0]['count']
                    counts[year] = count
                else:
                    return 0

                text += f"\n### Year {year} (Found: {count})\n"

                # If any articles were found and we have access to their data, take three sample
                # articles from the top of the table (title and journal name)
                if os.path.exists(articles_path) and count > 0:
                    papers = pd.read_csv(articles_path)
                    text += "Sample publications:\n"
                    for index, row in papers.head(3).iterrows():
                        title = row.get('title', 'No title')
                        journal = row.get('journal', 'No journal')
                        text += f"- {title} ({journal})\n"

            except Exception as e:
                text += f"\nError processing data for year {year}: {e}\n"

    # Check if each subsequent publication count is strictly greater (not equal!) to the previous one in the dictionary
    if list(counts.values()) == sorted(set(counts.values())):
        text += f"\nAn upward trend in the number of publications was observed."
    # Or if all values are equal
    elif len(set(counts.values())) == 1:
        text += f"\nNo upward or downward trend in the number of publications was observed."
    else:
        text += f"\nA downward trend in the number of publications was observed."

    return text, summaries


def create_report(config_path, output_report_file):
    """
    This function ties the other functions in the file together. Creates the comprehensive report string: divides the report into sections,
    loads the PM2.5 concentration exceedances table, calls the function that lists sample articles for each year
    and the number of found articles (hence we immediately see the literature trend).

    Args:
        config_path (str): path to the .yaml configuration file
        output_report_file (str): path to the file where the markdown report will be saved
    Returns:
    """
    # Load settings from the config file
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Sort years chronologically
    years = sorted(config.get('years'))

    report = "# Final Report: PM2.5 and Literature\n\n"
    report += f"Analyzed years: {years}\n\n"

    # Add the section regarding PM2.5 dust analysis
    report += "## Analysis of PM2.5 Exceedance Days\n"
    pm25_exceedances = load_pm25_exceedances(years)

    if pm25_exceedances:
        merged_pm25_exceedances = pd.concat(pm25_exceedances)
        report += merged_pm25_exceedances.to_markdown(index=False)
    else:
        report += "No PM2.5 data available or files have not been generated yet.\n"

    # Add the section regarding literature
    literature_section, summaries_list = generate_literature_section(years)
    report += literature_section

    # Save the report to a file
    os.makedirs(os.path.dirname(output_report_file), exist_ok=True)
    with open(output_report_file, "w", encoding="utf-8") as f:
        f.write(report)


if 'snakemake' in globals():
    # Check if the script was run by snakemake and call the main function
    create_report(
        config_path=snakemake.input.conf,
        output_report_file=snakemake.output.rep
    )