import yaml
import pandas as pd
import os
import sys
from Bio import Entrez
from Bio import Medline


def extract_year(date_str, default_year):
    """
    Parses the year from the DP (Date of Publication) medline field.

    Args:
        date_str (str): text date from the pubmed record, e.g., '2024 May 12'
        default_year (int): the year being processed (from config)
    Returns:
        year (str): year extracted from the pubmed record date
        default_year (str): if date parsing fails, returns the processed year from config
    """
    year = date_str[:4] if date_str else ""

    if year.isdigit() and len(year) == 4:
        return year
    return str(default_year)


def prepare_configuration(config_path, year):
    """
    Loads configuration from a file and prepares the query components to be sent to pubmed later.

    Args:
        config_path (str): path to the .yaml configuration file
        year (int): the year being processed
    Returns:
        max_results (int): maximum number of displayed found articles
        query_text (str): the query that will be sent to pubmed
    """
    # Load settings from the config file
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    pubmed_config = config.get("pubmed")
    query = pubmed_config.get("query")
    email = pubmed_config.get("email")
    max_results = pubmed_config.get("max_results")

    # Prepare the query for pubmed
    Entrez.email = email
    Entrez.tool = "BiopythonProject4"
    # Combine the keyword phrase with the specific publication year requirement using the [pdat] tag
    query_text = f"({query}) AND {year}[pdat]"

    return max_results, query_text


def execute_esearch(query_text, max_results):
    """
    Sends a query to pubmed, fetches the result and closes the query or exits the program on ESearch error.

    Args:
        query_text (str): the query that will be sent to pubmed
        max_results (int): maximum number of displayed found articles
    Returns:
        search_result: 'dictionary' of found articles for the sent query
    """
    try:
        search_query = Entrez.esearch(
            db="pubmed",
            term=query_text,
            retmax=max_results,
            usehistory="y"
        )
        search_result = Entrez.read(search_query)
        search_query.close()
        return search_result

    except Exception as e:
        print(f"ESearch error: {e}")
        sys.exit(1)


def fetch_records(search_result, max_results, year) -> list:
    """
    Based on the sent query, fetches data about specific articles from pubmed and saves them in a single list.

    Args:
        search_result: 'dictionary' of found articles for the sent query
        max_results (int): maximum number of displayed found articles
        year (int): the year being processed
    Returns:
        data (list): list of data fetched about the articles
    """
    # Save the features of the executed query - number of found articles, unique session identifier on the server
    # and the query number within this session
    count = int(search_result["Count"])
    webenv = search_result["WebEnv"]
    query_key = search_result["QueryKey"]

    # Create an empty list for data about found articles
    data = []

    # If any article is found, fetch the full record for each article
    if count > 0:
        try:
            record_batch = Entrez.efetch(
                db="pubmed",
                rettype="medline",
                retmode="text",
                retstart=0,
                retmax=max_results,
                webenv=webenv,
                query_key=query_key
            )

            # 'Cut' the batch of records into individual records
            records = Medline.parse(record_batch)

            # For each record, fetch the id, title, publication year, journal, authors, or exit the program
            # on EFetch/parsing error
            for record in records:
                pub_year = extract_year(record.get("DP"), year)

                data.append({
                    "pmid": record.get("PMID", "No pmid"),
                    "title": record.get("TI", "No title"),
                    "year": pub_year,
                    "journal": record.get("TA", "No journal"),
                    "authors": "; ".join(record.get("AU", ["No authors"]))
                })

            record_batch.close()

        except Exception as e:
            print(f"EFetch/parsing error: {e}")
            sys.exit(1)

    # Sort the results by pmid before returning to ensure determinism
    data.sort(key=lambda x: x["pmid"])

    return data


def save_results(data, year, output_papers_csv, output_summary_csv, output_top_journals_csv):
    """
    Aggregates found data and saves them to specific csv files.

    Args:
        data (list): list of data fetched about the articles
        year (int): the year being processed
        output_papers_csv (str): path to the file where data about found articles will be saved
        output_summary_csv (str): path to the file where the number of articles for the year will be saved
        output_top_journals_csv (str): path to the file where the top 10 journal names will be saved
    Returns:
    """
    # Create a pandas dataframe with data about the articles
    df_papers = pd.DataFrame(data, columns=["pmid", "title", "year", "journal", "authors"])

    # Create a folder based on the path to the output_papers_csv file
    os.makedirs(os.path.dirname(output_papers_csv), exist_ok=True)

    # Save data about articles to the output_papers_csv file
    df_papers.to_csv(output_papers_csv, index=False, encoding="utf-8")

    # Aggregate data about articles if they exist
    if not df_papers.empty:
        # Count the occurrences of each journal name and save it in a table
        top_journals = df_papers["journal"].value_counts().reset_index()
        top_journals.columns = ["journal", "count"]

        # Sort to ensure determinism
        top_journals = top_journals.sort_values(by=["count", "journal"], ascending=[False, True])

        # Save the 10 most frequently appearing journals to output_top_journals_csv
        top_journals.head(10).to_csv(output_top_journals_csv, index=False, encoding="utf-8")

        # Create a summary of the number of articles for the year
        summary = pd.DataFrame([{"year": year, "count": len(df_papers)}])

        # Save to the output_summary_csv file
        summary.to_csv(output_summary_csv, index=False, encoding="utf-8")
    else:
        # Save empty files to the specified paths as well
        pd.DataFrame(columns=["journal", "count"]).to_csv(output_top_journals_csv, index=False)
        pd.DataFrame([{"year": year, "count": 0}]).to_csv(output_summary_csv, index=False)


def fetch_pubmed_data(config_path, year, output_papers_csv, output_summary_csv, output_top_journals_csv):
    """
    This function ties the other functions in the file together. It prepares and sends a query to pubmed, then fetches
    information about found records, aggregates, and saves the results.

    Args:
        config_path (str): path to the .yaml configuration file
        year (int): the year being processed
        output_papers_csv (str): path to the file where data about found articles will be saved
        output_summary_csv (str): path to the file where the number of articles for the year will be saved
        output_top_journals_csv (str): path to the file where the top 10 journal names will be saved
    Returns:
    """
    # Prepare the configuration
    max_results, query_text = prepare_configuration(config_path, year)

    # ESearch
    search_result = execute_esearch(query_text, max_results)

    # EFetch
    data = fetch_records(search_result, max_results, year)

    # Save
    save_results(data, year, output_papers_csv, output_summary_csv, output_top_journals_csv)


if 'snakemake' in globals():
    # Check if the script was run by snakemake and call the main function
    fetch_pubmed_data(
        year=int(snakemake.wildcards.year),
        config_path=snakemake.params.conf_path,
        output_papers_csv=snakemake.output.papers,
        output_summary_csv=snakemake.output.summary,
        output_top_journals_csv=snakemake.output.journals
    )