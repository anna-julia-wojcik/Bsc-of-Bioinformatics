from src.literature.pubmed_fetch import extract_year

def test_extract_year_valid_date():
    """Checks the correct extraction of the year from a full date."""
    assert extract_year("2024 May 12", 2021) == "2024"

def test_extract_year_only_year():
    """Checks behavior for a string containing only the year."""
    assert extract_year("2019", 2021) == "2019"

def test_extract_year_invalid_data():
    """Checks if it returns the default year for invalid data."""
    assert extract_year("None", 2021) == "2021"
    assert extract_year(None, 2021) == "2021"

def test_extract_year_type_consistency():
    """Ensures that the result is always a string, even if the default is an int."""
    result = extract_year(None, 2024)
    assert isinstance(result, str)
    assert result == "2024"