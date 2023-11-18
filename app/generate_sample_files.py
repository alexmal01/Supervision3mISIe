# import os
# import pandas as pd
# from datetime import datetime, timedelta
# import random

# # Just for testing purposes

# # Tworzenie katalogów dla przykładowych danych
# base_directory = 'sample_data'
# os.makedirs(base_directory, exist_ok=True)

# # Zakłady dostępne w systemie
# available_plants = ['Zaklad1', 'Zaklad2', 'Zaklad3']

# # Okresy dostępne w systemie
# available_periods = ['2020', '2021', '2022']

# # Tworzenie przykładowych plików CSV
# for plant in available_plants:
#     for period in available_periods:
#         for file_type in range(1, 4):
#             # Tworzenie przykładowych danych
#             start_date = datetime(2023, 1, 1)
#             end_date = start_date + timedelta(days=30)
#             date_range = pd.date_range(start=start_date, end=end_date, freq='D')
#             values = [random.randint(1, 100) for _ in range(len(date_range))]
#             df = pd.DataFrame({'Date': date_range, 'Column1': values})

#             # Tworzenie katalogu dla zakładu, okresu i typu pliku
#             directory_path = os.path.join(base_directory, plant, period)
#             os.makedirs(directory_path, exist_ok=True)

#             # Zapisywanie danych do pliku CSV
#             file_path = os.path.join(directory_path, f'nazwa_{file_type}.csv')
#             df.to_csv(file_path, index=False)



# print("Przykładowe pliki zostały wygenerowane.")


import os
import pandas as pd
from datetime import datetime, timedelta
import random

# Just for testing purposes

# Tworzenie katalogów dla przykładowych danych
base_directory = 'sample_data'
os.makedirs(base_directory, exist_ok=True)

# Zakłady dostępne w systemie
available_plants = ['Zaklad1', 'Zaklad2', 'Zaklad3']

# Okresy dostępne w systemie
available_periods = ['2020', '2021', '2022']

def generate_type1_data(plant, period):
    start_date = datetime(2023, 1, 1)
    end_date = start_date + timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    values = [random.randint(1, 100) for _ in range(len(date_range))]
    df = pd.DataFrame({'ID_TAB': [random.randint(1, 100) for _ in range(len(date_range))],
                       'DATA SFCR': date_range,
                       'WERSJA SFCR': [random.randint(1, 10) for _ in range(len(date_range))],
                       'KOD ZAKŁADU': [random.randint(1, 10) for _ in range(len(date_range))],
                       'ID_SEKCJA NADRZĘDNA': [random.randint(1, 10) for _ in range(len(date_range))],
                       'ID_SEKCJA': [random.randint(1, 10) for _ in range(len(date_range))],
                       'NAZWA_SEKCJI': ['char' for _ in range(len(date_range))],
                       'LP.': [random.randint(1, 10) for _ in range(len(date_range))],
                       'TREŚĆ': ['char' for _ in range(len(date_range))]})
    
    # Save to CSV
    directory_path = os.path.join(base_directory, plant, period)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, 'Struktura dla danych jakościowych.csv')
    df.to_csv(file_path, index=False)

def generate_type2_data(plant, period):
    start_date = datetime(2023, 1, 1)
    end_date = start_date + timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    values = [random.randint(1, 100) for _ in range(len(date_range))]
    df = pd.DataFrame({'ID_TAB': [random.randint(1, 100) for _ in range(len(date_range))],
                       'DATA SFCR': date_range,
                       'WERSJA SFCR': [random.randint(1, 10) for _ in range(len(date_range))],
                       'KOD ZAKŁADU': [random.randint(1, 10) for _ in range(len(date_range))],
                       'FORMULARZ': ['char' for _ in range(len(date_range))],
                       'WIERSZ': ['char' for _ in range(len(date_range))],
                       'KOLUMNA': ['char' for _ in range(len(date_range))],
                       'TRZECI WYMIAR KRAJ': ['char' for _ in range(len(date_range))],
                       'WARTOŚĆ': [random.uniform(1, 100) for _ in range(len(date_range))]})

    # Save to CSV
    directory_path = os.path.join(base_directory, plant, period)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, 'Struktura dla obligatoryjnych tabel.csv')
    df.to_csv(file_path, index=False)

def generate_type3_data(plant, period):
    start_date = datetime(2023, 1, 1)
    end_date = start_date + timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame({'ID_TAB': [random.randint(1, 100) for _ in range(len(date_range))],
                       'DATA SFCR': date_range,
                       'WERSJA SFCR': [random.randint(1, 10) for _ in range(len(date_range))],
                       'KOD ZAKŁADU': [random.randint(1, 10) for _ in range(len(date_range))],
                       'ID_PYTANIA': [random.randint(1, 10) for _ in range(len(date_range))],
                       'CZY WYSTĄPIŁ KLUCZ (0/1)': [random.randint(0, 1) for _ in range(len(date_range))],
                       'LICZBA WYSTĄPIEŃ KLUCZY': [random.randint(1, 10) for _ in range(len(date_range))]})

    # Save to CSV
    directory_path = os.path.join(base_directory, plant, period)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, 'Struktura dla danych dla weryfikacji kompletności SFCR.csv')
    df.to_csv(file_path, index=False)

# Tworzenie przykładowych plików CSV
for plant in available_plants:
    for period in available_periods:
        generate_type1_data(plant, period)
        generate_type2_data(plant, period)
        generate_type3_data(plant, period)

print("Przykładowe pliki zostały wygenerowane.")