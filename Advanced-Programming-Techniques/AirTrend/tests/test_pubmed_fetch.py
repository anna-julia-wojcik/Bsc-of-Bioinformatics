import pytest
from src.literature.pubmed_fetch import wyciagnij_rok

def test_wyciagnij_rok_valid_date():
    """Sprawdza poprawne wyciąganie roku z pełnej daty."""
    assert wyciagnij_rok("2024 May 12", 2021) == "2024"

def test_wyciagnij_rok_only_year():
    """Sprawdza zachowanie dla samego roku."""
    assert wyciagnij_rok("2019", 2021) == "2019"

def test_wyciagnij_rok_invalid_data():
    """Sprawdza, czy zwraca domyślny rok dla błędnych danych."""
    assert wyciagnij_rok("Brak", 2021) == "2021"
    assert wyciagnij_rok(None, 2021) == "2021"

def test_wyciagnij_rok_type_consistency():
    """Upewnia się, że wynik to zawsze string, nawet jeśli domyślny to int."""
    wynik = wyciagnij_rok(None, 2024)
    assert isinstance(wynik, str)
    assert wynik == "2024"