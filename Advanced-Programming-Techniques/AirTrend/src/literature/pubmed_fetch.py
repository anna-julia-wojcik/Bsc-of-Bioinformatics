import yaml
import pandas as pd
import os
import sys
from Bio import Entrez
from Bio import Medline


def wyciagnij_rok(data_str, domyslny_rok):
    """
    Parsuje rok z pola DP (Date of Publication) medline.

    Args:
        data_str (str): tekstowa data z rekordu pubmed, np. '2024 May 12'
        domyslny_rok (int): rok, dla którego rozpatrywane są dane (config)
    Returns:
        rok (str): rok wyciągnięty z daty z rekordu pubmed
        domyslny_rok (str): jeśli nie udało się sparsować daty, zwraca rozpatrywany rok z configu
    """
    rok = data_str[:4] if data_str else ""

    if rok.isdigit() and len(rok) == 4:
        return rok
    return str(domyslny_rok)


def przygotuj_konfiguracje(config_path, rok):
    """
    Pobiera konfiguracje z pliku i przygotowuje składowe zapytania wysyłanego później do pubmedu.

    Args:
        config_path (str): ścieżka do konfiguracji z pliku .yaml
        rok (int): rok, dla którego rozpatrywane są dane
    Returns:
        max_results (int): maksymalna liczba wyświetlanych znalezionych artykułów
        tekst_zapytania (str): zapytanie, które zostanie wysłane do pubmedu
    """
    # Wczytujemy ustawienia z pliku config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    pubmed_config = config.get("pubmed")
    query = pubmed_config.get("query")
    email = pubmed_config.get("email")
    max_results = pubmed_config.get("max_results")

    # Przygotowujemy zapytanie do pubmedu
    Entrez.email = email
    Entrez.tool = "BiopythonProject4"
    # Łączymy frazę kluczową z wymogiem konkretnego roku publikacji przy użyciu tagu [pdat]
    tekst_zapytania = f"({query}) AND {rok}[pdat]"

    return max_results, tekst_zapytania


def wykonaj_esearch(tekst_zapytania, max_results):
    """
    Wysyła zapytanie do pubmedu, pobiera wynik i zamyka zapytanie lub kończy działanie programu przy błędzie ESearch.

    Args:
        tekst_zapytania (str): zapytanie, które zostanie wysłane do pubmedu
        max_results (int): maksymalna liczba wyświetlanych znalezionych artykułów
    Returns:
        wynik_zapytania: 'słownik' znalezionych artykułów dla wysłanego zapytania
    """
    try:
        zapytanie = Entrez.esearch(
            db="pubmed",
            term=tekst_zapytania,
            retmax=max_results,
            usehistory="y"
        )
        wynik_zapytania = Entrez.read(zapytanie)
        zapytanie.close()
        return wynik_zapytania

    except Exception as e:
        print(f"Błąd ESearch: {e}")
        sys.exit(1)


def pobierz_rekordy(wynik_zapytania, max_results, rok) -> list:
    """
    Na podstawie wysłanego zapytania, pobiera dane o konkretnych artykułach z pubmedu i zapisuje je w jednej liście.

    Args:
        wynik_zapytania: 'słownik' znalezionych artykułów dla wysłanego zapytania
        max_results (int): maksymalna liczba wyświetlanych znalezionych artykułów
        rok (int): rok, dla którego rozpatrywane są dane
    Returns:
        data (list): lista danych pobranych o artykułach
    """
    # Zapisujemy cechy wykonanego zapytania - ilość znalezionych artykułów, unikalny identyfikator sesji na serwerze
    # i numer zapytania wewnątrz tej sesji
    count = int(wynik_zapytania["Count"])
    webenv = wynik_zapytania["WebEnv"]
    query_key = wynik_zapytania["QueryKey"]

    # Tworzymy pustą listę na dane o znalezionych artykułach
    data = []

    # Jeśli znaleziono jakikolwiek artykuł, pobieramy pełny rekord dla każdego artykułu
    if count > 0:
        try:
            zbior_rekordow = Entrez.efetch(
                db="pubmed",
                rettype="medline",
                retmode="text",
                retstart=0,
                retmax=max_results,
                webenv=webenv,
                query_key=query_key
            )

            # 'Tniemy' zbiór rekordów na pojedyncze rekordy
            rekordy = Medline.parse(zbior_rekordow)

            # Dla każdego rekordu pobieramy dane id, tytuł, rok publikacji, journal, autorów  lub kończymy działanie
            # programu przy błędzie EFetch/parsowania
            for rekord in rekordy:
                pub_rok = wyciagnij_rok(rekord.get("DP"), rok)

                data.append({
                    "pmid": rekord.get("PMID", "No pmid"),
                    "title": rekord.get("TI", "No title"),
                    "year": pub_rok,
                    "journal": rekord.get("TA", "No journal"),
                    "authors": "; ".join(rekord.get("AU", ["No authors"]))
                })

            zbior_rekordow.close()

        except Exception as e:
            print(f"Błąd EFetch/parsowania: {e}")
            sys.exit(1)

    # Sortujemy wyniki po pmid przed zwróceniem dla zapewnienia determinizmu
    data.sort(key=lambda x: x["pmid"])

    return data


def zapisz_wyniki(data, rok, output_artykuly_csv, output_podsumowanie_csv, output_top_czasopisma_csv):
    """
    Agreguje znalezione dane i zapisuje je do konkretnych plików csv.

    Args:
        data (list): lista danych pobranych o artykułach
        rok (int): rok, dla którego rozpatrywane są dane
        output_artykuly_csv (str): ścieżka do pliku, gdzie zostaną zapisane dane o znalezionych artykułach
        output_podsumowanie_csv (str): ścieżka do pliku, gdzie zostanie zapisana ilość artykułów dla roku
        output_top_czasopisma_csv (str): ścieżka do pliku, gdzie zostanie zapisane top 10 nazw czasopism
    Returns:
    """
    # Tworzymy dataframe w pandas z danymi o artykułach
    df_artykuly = pd.DataFrame(data, columns=["pmid", "title", "year", "journal", "authors"])

    # Tworzymy folder na podstawie ścieżki do pliku output_artykuly_csv
    os.makedirs(os.path.dirname(output_artykuly_csv), exist_ok=True)

    # Zapisujemy dane o artykłuach do pliku output_artykuly_csv
    df_artykuly.to_csv(output_artykuly_csv, index=False, encoding="utf-8")

    # Agregujemy dane o artykułach, jeśli takie istnieją
    if not df_artykuly.empty:
        # Liczymy wystąpienia nazwy każdego czasopisma i zapisujemy w tabelę
        top_czasopisma = df_artykuly["journal"].value_counts().reset_index()
        top_czasopisma.columns = ["journal", "count"]

        # Sortujemy dla zapewnienia determinizmu
        top_czasopisma = top_czasopisma.sort_values(by=["count", "journal"], ascending=[False, True])

        # Zapisujemy 10 najczęściej pojawiających się czasopism do output_top_czasopisma_csv
        top_czasopisma.head(10).to_csv(output_top_czasopisma_csv, index=False, encoding="utf-8")

        # Tworzymy podsumowanie ilości artykułów dla roku
        podsumowanie = pd.DataFrame([{"year": rok, "count": len(df_artykuly)}])

        # Zapisujemy do pliku output_podsumowanie_csv
        podsumowanie.to_csv(output_podsumowanie_csv, index=False, encoding="utf-8")
    else:
        # Puste pliki też zapisujemy pod wskazane ścieżki
        pd.DataFrame(columns=["journal", "count"]).to_csv(output_top_czasopisma_csv, index=False)
        pd.DataFrame([{"year": rok, "count": 0}]).to_csv(output_podsumowanie_csv, index=False)


def pobierz_dane_pubmed(config_path, rok, output_artykuly_csv, output_podsumowanie_csv, output_top_czasopisma_csv):
    """
    Funkcja spina pozostałe funkcje z pliku w jedność. Przygotowuje i wysyła zapytanie do pubmedu, potem pobiera
    informacje o znalezionych rekordach i agreguje oraz zapisuje wyniki.

    Args:
        config_path (str): ścieżka do konfiguracji z pliku .yaml
        rok (int): rok, dla którego rozpatrywane są dane
        output_artykuly_csv (str): ścieżka do pliku, gdzie zostaną zapisane dane o znalezionych artykułach
        output_podsumowanie_csv (str): ścieżka do pliku, gdzie zostanie zapisana ilość artykułów dla roku
        output_top_czasopisma_csv (str): ścieżka do pliku, gdzie zostanie zapisane top 10 nazw czasopism
    Returns:
    """
    # Przygotowujemy konfigurację
    max_results, tekst_zapytania = przygotuj_konfiguracje(config_path, rok)

    # ESearch
    wynik_zapytania = wykonaj_esearch(tekst_zapytania, max_results)

    # EFetch
    data = pobierz_rekordy(wynik_zapytania, max_results, rok)

    # Zapisujemy
    zapisz_wyniki(data, rok, output_artykuly_csv, output_podsumowanie_csv, output_top_czasopisma_csv)


if 'snakemake' in globals():
    # Sprawdzamy, czy skrypt został uruchomiony przez snakemake i wywołujemy główną funkcję
    pobierz_dane_pubmed(
        rok=int(snakemake.wildcards.year),
        config_path=snakemake.params.conf_path,
        output_artykuly_csv=snakemake.output.papers,
        output_podsumowanie_csv=snakemake.output.summary,
        output_top_czasopisma_csv=snakemake.output.journals
    )


