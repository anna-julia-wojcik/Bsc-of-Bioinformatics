import os
import yaml
import pandas as pd

import wczytywanie_i_czyszczenie_danych as wicd
import grouped_barplot as gbp


def wybierz_miasta(df: pd.DataFrame, config) -> pd.DataFrame:
    """
    Pobiera miasta podane w konfiguracjach i odfiltrowuje te stacje, które są miastami zgodnymi z tymi w konfiguracjach.

    Args:
        df (pd.DataFrame): dane, z których trzeba odfiltrować konkretne miasta
        config: konfiguracje wczytane z pliku .yaml
    Returns:
        df (pd.DataFrame): dane z odfiltrowanymi konkretnymi miastami
    """
    # Wczytujemy ustawienia z pliku config
    miasta = config.get("cities", ["Warszawa", "Katowice"])
    kolumny_do_zostawienia = []

    # Nazwa kolumny z datą, której szuka późniejsza funkcja
    kolumna_daty = 'Miejscowość_Kod stacji'

    for col in df.columns:
        # Jeśli to kolumna z datą, zostawiamy ją
        if col == kolumna_daty:
            kolumny_do_zostawienia.append(col)
            continue

        # Resztę filtrujemy po miastach
        for miasto in miasta:
            if miasto in col:
                kolumny_do_zostawienia.append(col)
                break

    if kolumny_do_zostawienia:
        df = df[kolumny_do_zostawienia]

    return df


def przygotuj_konfiguracje(config_path, rok):
    """
    Pobiera konfiguracje z pliku i przygotowuje dane potrzebne do scrapingu ze strony gios.

    Args:
        config_path (str): ścieżka do konfiguracji z pliku .yaml
        rok (int): rok, dla którego rozpatrywane są dane
    Returns:
        config: konfiguracje wczytane z pliku .yaml
        gios_archive_url (str): ścieżka do strony do pobierania danych
        gios_url_ids (dict): oryginalne id dla każdego roku przy pobieraniu danych
        gios_pm25_file (dict): oryginalne nazwy plików excela dla każdego roku przy pobieraniu danych
    """
    # Wczytujemy ustawienia z pliku config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
    gios_url_ids = {2015: '236', 2018: '603', 2019: '322', 2021: '486', 2024: '582'}
    gios_pm25_file = {2015: '2015_PM25_1g.xlsx', 2018: '2018_PM25_1g.xlsx', 2019: '2019_PM25_1g.xlsx',
                      2021: '2021_PM25_1g.xlsx', 2024: '2024_PM25_1g.xlsx'}

    if rok not in gios_url_ids:
        raise ValueError(f"Brak danych dla roku {rok}")

    return config, gios_archive_url, gios_url_ids, gios_pm25_file


def pobierz_i_oczysc_dane(rok, config, gios_archive_url, gios_url_ids, gios_pm25_file) -> pd.DataFrame:
    """
    Scrapuje dane ze strony gios, czyści i łączy pliki oraz odfiltrowuje dane dla konkretnych miast.

    Args:
        rok (int): rok, dla którego rozpatrywane są dane
        config: konfiguracje wczytane z pliku .yaml
        gios_archive_url (str): ścieżka do strony do pobierania danych
        gios_url_ids (dict): orginalne id dla każdego roku przy pobieraniu danych
        gios_pm25_file (dict): orginalne nazwy plików excela dla każdego roku przy pobieraniu danych
    Returns:
        dfs_dla_miast (pd.DataFrame): oczyszczone dane odfiltrowane tylko dla konkretnego roku i miast
    """
    # Pobieranie i czyszczenie danych (dla jednego roku)
    dane_dla_roku = {rok: wicd.download_gios_archive(rok, gios_url_ids[rok], gios_archive_url, gios_pm25_file[rok])}
    metadane = wicd.download_metadane('622', gios_archive_url, 'Metadane oraz kody stacji i stanowisk pomiarowych.xlsx')

    dfs_obrobione = wicd.wyczysc_pliki(dane_dla_roku, metadane)
    dfs_polaczone = wicd.polacz_dfs(dfs_obrobione)
    dfs_dla_miast = wybierz_miasta(dfs_polaczone, config)

    return dfs_dla_miast


def oblicz_i_zapisz_wyniki(dfs_dla_miast, rok, output_przekroczenia_csv, output_srednie_csv):
    """
    Wywołuje funkcje obliczające liczbę dni z przekroczeniem normy PM2.5 oraz średnie dzienne, następnie zapisuje je
    do plików.

    Args:
        dfs_dla_miast (pd.DataFrame): oczyszczone dane odfiltrowane tylko dla konkretnego roku i miast
        rok (int): rok, dla którego rozpatrywane są dane
        output_przekroczenia_csv (str): ścieżka do pliku, gdzie zostaną zapisane dane o przekroczeniach
        output_srednie_csv (str): ścieżka do pliku, gdzie zostaną zapisane dane o średnich dziennych
    Returns:
    """
    # Upewniamy się, że folder wyjściowy istnieje
    os.makedirs(os.path.dirname(output_przekroczenia_csv), exist_ok=True)

    # Liczymy średnie dobowe
    df_daily = gbp.policz_srednie_dzienne(dfs_dla_miast)
    df_daily.reset_index(names=["Data"]).to_csv(output_srednie_csv, sep=';', decimal=',', header=True, index=False,
                                                encoding="utf-8")

    # Liczymy dni z przekroczeniami normy
    df_przekroczenia = gbp.policz_dni_z_przekroczeniem(df_daily, [rok])
    df_przekroczenia.reset_index(names=["Rok"]).to_csv(output_przekroczenia_csv, sep=';', decimal=',', header=True, index=False, encoding="utf-8")


def analiza_wybranego_roku(rok, config_path, output_przekroczenia_csv, output_srednie_csv):
    """
    Funkcja spina pozostałe funkcje z pliku w jedność. Wczytuje, oczyśczcza, filtruje i zapisuje dane.

    Args:
        rok (int): rok, dla którego rozpatrywane są dane
        config_path (str): ścieżka do konfiguracji z pliku .yaml
        output_przekroczenia_csv (str): ścieżka do pliku, gdzie zostaną zapisane dane o przekroczeniach
        output_srednie_csv (str): ścieżka do pliku, gdzie zostaną zapisane dane o średnich dziennych
    Returns:
    """
    # Konfiguracja
    config, gios_archive_url, gios_url_ids, gios_pm25_file = przygotuj_konfiguracje(config_path, rok)

    # Pobieramy, czyścimy i zapisujemy dane
    dfs_dla_miast = pobierz_i_oczysc_dane(rok, config, gios_archive_url, gios_url_ids, gios_pm25_file)
    oblicz_i_zapisz_wyniki(dfs_dla_miast, rok, output_przekroczenia_csv, output_srednie_csv)


if 'snakemake' in globals():
    # Sprawdzamy, czy skrypt został uruchomiony przez snakemake i wywołujemy główną funkcję
    analiza_wybranego_roku(
        rok=int(snakemake.wildcards.year),
        config_path=snakemake.params.conf_path,
        output_przekroczenia_csv=snakemake.output.exc,
        output_srednie_csv=snakemake.output.daily
    )