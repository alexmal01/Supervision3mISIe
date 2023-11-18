import os
import pandas as pd
from datetime import datetime, timedelta
import random

# Just for testing purposes

# Tworzenie katalogów dla przykładowych danych
base_directory = 'sample_data'
os.makedirs(base_directory, exist_ok=True)

# Zakłady dostępne w systemie
available_plants = ['Plant1', 'Plant2', 'Plant3']

# Okresy dostępne w systemie
available_periods = ['Period1', 'Period2', 'Period3']

# Tworzenie przykładowych plików CSV
for plant in available_plants:
    for period in available_periods:
        for file_type in range(1, 4):
            # Tworzenie przykładowych danych
            start_date = datetime(2023, 1, 1)
            end_date = start_date + timedelta(days=30)
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            values = [random.randint(1, 100) for _ in range(len(date_range))]
            df = pd.DataFrame({'Date': date_range, 'Column1': values})

            # Tworzenie katalogu dla zakładu, okresu i typu pliku
            directory_path = os.path.join(base_directory, plant, period)
            os.makedirs(directory_path, exist_ok=True)

            # Zapisywanie danych do pliku CSV
            file_path = os.path.join(directory_path, f'nazwa_{file_type}.csv')
            df.to_csv(file_path, index=False)

print("Przykładowe pliki zostały wygenerowane.")
