# AirTrend

Projekt stanowi zautomatyzowany potok przetwarzania danych (pipeline) zarządzany przez narzędzie Snakemake. <br>
Integruje on analizę danych środowiskowych (stężenia PM2.5 z GIOŚ) z analizą bibliometryczną literatury medycznej (PubMed) w celu zbadania korelacji między jakością powietrza a trendami w publikacjach naukowych w latach zdefiniowanych w konfiguracji (np. 2019, 2024).

## Etapy projektu

- Automatyzacja przepływu pracy przy użyciu Snakemake.
- Pobieranie i czyszczenie danych o zawartości PM2.5 (wykorzystanie modułów z Projektu 3).
- Pobieranie metadanych publikacji naukowych z bazy PubMed przy użyciu API Entrez.
- Generowanie automatycznego raportu końcowego w formacie Markdown.

## Instalacja i wymagania

Projekt wymaga Pythona ≥ 3.8. Wszystkie zależności znajdują się w `requirements.txt`.  
Do zainstalowania poleceniem:

```bash
pip install -r requirements.txt
```

# Uruchamianie

## Konfiguracja

Pipeline jest konfigurowany przez plik `config.yaml`. Użytkownik może dowolnie zmieniać:

- zakres lat (`years`)
- listę miast (`cities`)
- parametry zapytania do PubMed (`query`, `email`, `max_results`)

Przykładowy plik konfiguracyjny:

```yaml
years: [2019, 2024]
cities: ["Warszawa", "Katowice"]

pubmed:
  query: "PM2.5 Poland"
  email: "a.wojcik55@student.uw.edu.pl"
  max_results: 20
```

Można podać inne lata (np. `[2018, 2020]`), inne miasta lub zmienić zapytanie do PubMed.

## Uruchomienie pipeline

Pipeline uruchamiamy poleceniem:

```bash
snakemake -s Snakefile_task4 --cores 1
```

Parametr `--cores` określa liczbę rdzeni CPU wykorzystywanych do obliczeń (można zwiększyć, jeśli dostępne są zasoby).

## Bonus

W trakcie realizacji projektu zidentyfikowano zmianę w specyfikacji argumentów nowszych wersji narzędzia Snakemake.

Próba jawnego wymuszenia weryfikacji opartej wyłącznie na sumach kontrolnych za pomocą polecenia:

```bash
snakemake -s Snakefile_task4 --cores 1 --rerun-triggers checksum
```
zakończy się błędem walidacji argumentów (`invalid choice`). W aktualnej wersji oprogramowania mechanizm `checksum` przestał być samodzielną opcją konfiguracyjną, stając się integralną częścią wewnętrznej logiki weryfikacji (implementowaną w ramach trybu `mtime` lub `input`).

Zgodnie z dokumentacją techniczną Snakemake:

> **--rerun-triggers**
> Possible choices: code, input, mtime, params, software-env
> Define what triggers the rerunning of a job. By default, all triggers are used, which guarantees that results are consistent with the workflow code and configuration. If you rather prefer the traditional way of just considering file modification dates, use **--rerun-trigger mtime**.

W związku z powyższym, w instrukcji uruchomienia projektu rekomendowane jest wykorzystanie flagi `mtime` lub ustawień domyślnych. Podejście to zapewnia poprawną weryfikację spójności danych (w tym sprawdzenie metadanych plików) bez generowania błędów składniowych.

# Scenariusze uruchomienia

## Scenariusz 1

Użytkownik ustawia w `config.yaml`:

```yaml
years: [2021, 2024]
```

Następnie uruchamia:

```bash
snakemake -s Snakefile_task4 --cores 1
```

Pipeline wykonuje pełne przetwarzanie dla obu lat:
- oblicza PM2.5 dla 2021 i 2024,
- pobiera i analizuje dane PubMed dla 2021 i 2024,
- generuje raport obejmujący lata {2021, 2024}.

Poprawność wykonania weryfikuję na podstawie logów Snakemake (widoczne uruchomienie reguł dla obu lat) oraz obecności wygenerowanych plików wynikowych i raportu dla {2021, 2024}.


## Scenariusz 2 (inkrementalne wykonanie)

Użytkownik zmienia konfigurację na:

```yaml
years: [2019, 2024]
```

i ponownie uruchamia:

```bash
snakemake -s Snakefile_task4 --cores 1
```

Pipeline wykonuje tylko brakujące kroki:
- oblicza PM2.5 dla 2019 (2024 zostaje pominięty),
- pobiera i analizuje dane PubMed dla 2019 (2024 zostaje pominięty),
- generuje nowy raport dla {2019, 2024}.

Weryfikacja odbywa się na podstawie logów Snakemake (brak ponownego uruchamiania reguł dla 2024, widać po jobids, że Snakemake ma mniej zadań do wykonania, bo nie tworzy plików dla 2024)

# Opis działania modułów

## 1. Snakefile_task4

### Wejście:
- plik konfiguracyjny `config/task4.yaml`
- lata zdefiniowane w `config["years"]`
- parametry zapytania do PubMed z sekcji `pubmed`

### Wyjście:
- pliki wynikowe PM2.5 w `results/pm25/{year}/`
- pliki wynikowe PubMed w `results/literature/{year}/`
- raport końcowy `results/report/raport_task4.md`

### Logika działania:

`Snakefile_task4` definiuje workflow w Snakemake i zarządza zależnościami między etapami analizy.  

Dla każdego roku z konfiguracji:
1. uruchamia analizę danych PM2.5,
2. uruchamia pobieranie i analizę literatury z PubMed,
3. po zakończeniu wszystkich analiz generuje raport końcowy.

Reguła `all` wskazuje raport jako cel końcowy pipeline. Snakefile działa inkrementalnie.

## 2. pubmed_fetch.py

### Wejście:
- plik konfiguracyjny `config/task4.yaml`
- rok przekazany przez Snakemake (`{year}`)
- parametry z sekcji `pubmed`:
  - `query`
  - `email`
  - `max_results`

### Wyjście:
- `results/literature/{year}/pubmed_papers.csv`
- `results/literature/{year}/summary_by_year.csv`
- `results/literature/{year}/top_journals.csv`

### Logika działania:

Moduł pobiera i analizuje artykuły z bazy PubMed dla wskazanego roku.

1. Odczytuje konfigurację i buduje zapytanie w formie:
   `(query) AND {rok}[pdat]`.
2. Wysyła zapytanie do PubMed (ESearch), a następnie pobiera pełne rekordy artykułów (EFetch).
3. Z każdego rekordu wyciąga:
   - PMID,
   - tytuł,
   - rok publikacji,
   - nazwę czasopisma,
   - autorów.
4. Sortuje dane dla zapewnienia determinizmu wyników.
5. Zapisuje:
   - pełną listę artykułów do `pubmed_papers.csv`,
   - liczbę artykułów w danym roku do `summary_by_year.csv`,
   - 10 najczęściej występujących czasopism do `top_journals.csv`.

Skrypt jest uruchamiany przez Snakemake osobno dla każdego roku zdefiniowanego w pliku konfiguracyjnym.

## 3. project3_main.py

### Wejście:
- plik konfiguracyjny `config/task4.yaml`
- rok przekazany przez Snakemake (`{year}`)
- dane archiwalne PM2.5 z GIOŚ dla wskazanego roku
- metadane stacji pomiarowych
- lista miast z sekcji `cities` w konfiguracji

### Wyjście:
- `results/pm25/{year}/daily_means.csv`
- `results/pm25/{year}/exceedance_days.csv`

### Logika działania:

Moduł odpowiada za pobranie, oczyszczenie i analizę danych PM2.5 dla wybranego roku.

1. Wczytuje konfigurację oraz przygotowuje adresy do pobrania danych archiwalnych GIOŚ.
2. Pobiera dane godzinowe PM2.5 oraz metadane stacji.
3. Czyści i łączy dane, a następnie filtruje je do miast wskazanych w konfiguracji.
4. Oblicza:
   - średnie dobowe stężeń PM2.5,
   - liczbę dni z przekroczeniem normy.
5. Zapisuje wyniki do plików CSV w katalogu `results/pm25/{year}/`.

Skrypt jest uruchamiany przez Snakemake osobno dla każdego roku zdefiniowanego w pliku konfiguracyjnym.

## 4. create_report.py

### Wejście:
- plik konfiguracyjny `config/task4.yaml`
- pliki wynikowe PM2.5:
  - `results/pm25/{year}/exceedance_days.csv`
- pliki wynikowe PubMed:
  - `results/literature/{year}/pubmed_papers.csv`
  - `results/literature/{year}/summary_by_year.csv`

### Wyjście:
- raport końcowy w formacie Markdown: `results/report/raport_task4.md`

### Logika działania:

Moduł generuje końcowy raport łączący wyniki analizy PM2.5 oraz literatury PubMed.

1. Wczytuje konfigurację i ustala lata do analizy.
2. Łączy dane o przekroczeniach PM2.5 z poszczególnych lat i wstawia je do raportu.
3. Dla każdego roku analizuje pliki PubMed, podsumowuje liczbę artykułów i wybiera kilka przykładowych publikacji.
4. Tworzy w raporcie sekcje:
   - dni z przekroczeniami PM2.5,
   - przegląd literatury z PubMed wraz z trendami publikacji.
5. Zapisuje raport do wskazanego pliku Markdown.
   
Skrypt jest wywoływany przez Snakemake raz, po zakończeniu wszystkich analiz PM2.5 i PubMed dla wskazanych lat.

## 5.test_pubmed_fetch.py

### Wejście:
- funkcja `wyciagnij_rok` z modułu `pubmed_fetch.py`
- przykładowe wartości dat w różnych formatach:
  - pełna data: `"2024 May 12"`
  - tylko rok: `"2019"`
  - niepoprawne wartości: `"Brak"`, `None`

### Wyjście:
- wynik funkcji `wyciagnij_rok` jako string reprezentujący rok publikacji

### Logika działania:
Moduł testowy sprawdza poprawność funkcji parsującej rok z rekordu PubMed.  

Testy obejmują:
1. Poprawne wyciąganie roku z pełnej daty.
2. Wyciąganie roku, gdy podany jest tylko numer roku.
3. Zwracanie domyślnego roku z konfiguracji w przypadku niepoprawnych danych lub braku daty.
4. Sprawdzenie spójności typu wyniku (zawsze string).  

Test uruchamia się poleceniem:

```bash
python -m pytest tests/test_pubmed_fetch.py
```
