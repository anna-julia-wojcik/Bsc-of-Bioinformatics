import pandas as pd
import os
import yaml


def wczytaj_przekroczenia_pm25(lata):
    """
    Wczytuje dane o przekroczeniach stężeń PM2.5 dla podanych lat.

    Args:
        lata (list): lista lat rozpatrywanych przy pobieraniu danych
    Returns:
        wszystkie_pm25 (list): lista DataFrame'ów przekroczeń stężeń dla lat przekazanych w argumencie
    """
    wszystkie_pm25 = []

    for rok in lata:
        sciezka = f"results/pm25/{rok}/exceedance_days.csv"
        if os.path.exists(sciezka):
            try:
                df = pd.read_csv(sciezka, sep=';')
                wszystkie_pm25.append(df)
            except Exception as e:
                print(f"Nie udało się wczytać {sciezka}: {e}")

    return wszystkie_pm25


def generuj_sekcje_literatury(lata):
    """
    Na podstawie istniejących plików odnośnie danych pobranych z pubmedu, przygotowuje w markdown sekcję raportu
    odnośnie ilości publikacji znalezionych dla konkretnych lat oraz 3 przykładowe artykuły z tych lat.

    Args:
        lata (list): lista lat rozpatrywanych przy pobieraniu danych
    Returns:
        tekst (str): przygotowany tekst raportu w formacie markdown
        podsumowania (list): lista ilości artykułów znalezionych dla konkretnych lat
    """
    tekst = "\n\n## Przegląd Literatury (PubMed)\n"
    podsumowania = []
    ilosci = {}

    for rok in lata:
        sciezka_podsumowanie = f"results/literature/{rok}/summary_by_year.csv"
        sciezka_artykuly = f"results/literature/{rok}/pubmed_papers.csv"

        if os.path.exists(sciezka_podsumowanie):
            try:
                podsumowanie = pd.read_csv(sciezka_podsumowanie)
                podsumowania.append(podsumowanie)

                # Pobieramy informację, ile publikacji ogólnie znaleziono dla danego roku
                if not podsumowanie.empty:
                    ilosc = podsumowanie.iloc[0]['count']
                    ilosci[rok] = ilosc
                else:
                    return 0

                tekst += f"\n### Rok {rok} (Znaleziono: {ilosc})\n"

                # Jeśli znaleziono jakiekolwiek artykuły i mamy dostęp do danych o nich, bierzemy trzy przykładowe
                # artykuły z góry tabeli (tytuł i nazwę czasopisma)
                if os.path.exists(sciezka_artykuly) and ilosc > 0:
                    papers = pd.read_csv(sciezka_artykuly)
                    tekst += "Przykładowe publikacje:\n"
                    for column, row in papers.head(3).iterrows():
                        tytul = row.get('title', 'Brak tytułu')
                        gazeta = row.get('journal', 'Brak czasopisma')
                        tekst += f"- {tytul} ({gazeta})\n"

            except Exception as e:
                tekst += f"\nBłąd przetwarzania danych dla roku {rok}: {e}\n"

    # Sprawdzamy czy każda kolejna ilość publikacji jest ostro większa (nie równa!) od poprzedniej w słowniku
    if list(ilosci.values()) == sorted(set(ilosci.values())):
        tekst += f"\nZauważono trend wzrostowy w liczbie publikacji."
    # Lub czy wszystkie wartości są sobie równe
    elif len(set(ilosci.values())) == 1:
        tekst += f"\nNie zauważono trendu wzrostowego ani malejącego w liczbie publikacji."
    else:
        tekst += f"\nZauważono trend malejący w liczbie publikacji."

    return tekst, podsumowania


def stworz_raport(config_path, output_raport_csv):
    """
    Funkcja spina pozostałe funkcje z pliku w jedność. Tworzy całościowy string raportu: dzieli raport na sekcje,
    wczytuje tabelę przekroczeń stężeń PM2.5, wywołuje funkcję wypisującą przykładowe artykuły dla każdego roku
    i liczbę znalezionych artykułów (stąd od razu widzimy trend literaturowy).

    Args:
        config_path (str): ścieżka do konfiguracji z pliku .yaml
        output_raport_csv (str): ścieżka do pliku, gdzie zostanie zapisany raport w markdown
    Returns:
    """
    # Wczytujemy ustawienia z pliku config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Sortujemy lata chronologicznie
    lata = sorted(config.get('years'))

    raport = "# Raport Końcowy: PM2.5 i Literatura\n\n"
    raport += f"Analizowane lata: {lata}\n\n"

    # Dodajemy część odnośnie analizy pyłów PM2.5
    raport += "## Analiza ilości dni przekroczeń stężeń PM2.5\n"
    przekroczenia_pm25 = wczytaj_przekroczenia_pm25(lata)

    if przekroczenia_pm25:
        polaczone_przekroczenia_pm25 = pd.concat(przekroczenia_pm25)
        raport += polaczone_przekroczenia_pm25.to_markdown(index=False)
    else:
        raport += "Brak danych PM2.5 lub pliki nie zostały jeszcze wygenerowane.\n"

    # Dodajemy część odnośnie literatury
    sekcja_literatury, lista_podsumowan = generuj_sekcje_literatury(lata)
    raport += sekcja_literatury

    # Zapisujemy raport do pliku csv
    os.makedirs(os.path.dirname(output_raport_csv), exist_ok=True)
    with open(output_raport_csv, "w", encoding="utf-8") as f:
        f.write(raport)


if 'snakemake' in globals():
    # Sprawdzamy, czy skrypt został uruchomiony przez snakemake i wywołujemy główną funkcję
    stworz_raport(
        config_path=snakemake.input.conf,
        output_raport_csv=snakemake.output.rep
    )