# Supervision3mISIe

## Moduły

### Cracker

Moduł do procesowania zebranych danych - tabularyzacji, wyszukiwania wzorców i rozpoznawania obiektów w plikach.

### Dashboard

Napisany w Dashu - służy do jasnej i przejrzystej prezentacji wyników naszej pracy. Instrukcja uruchomienia znajduje się na dole tego pliku.

### Scraper
Moduł składa się z 2 submodułów. Napisany przy wykorzystaniu biblioteki Beautiful Soup 4 w Pythonie. 

#### Pobieranie linków
Funkcja pobierania linków pracuje wielokątkowo (domyślnie jest to 6 linków per wątek, czyli w przypadku zadania potrzeba 9 wątków).
Przyjmuje listę linków. Tworzy pliki JSON zawierające:
 * `klucz` - url
 * `wartość` - true/false w zależności czy dana strona została odwiedziona
Wątki odwiedzają kolejne nieodwiedzone podstrony danej wejściowej domeny z listy. Każda wejściowa domena posiada timeout (domyślnie 30 minut), który ogranicza sytuacje wolnego połączenia do strony.

#### Pobieranie PDFów
Za pomocą słów kluczowych w linkach pobierane są odpowiednie PDFy z plikami SFCR oraz z audytami. Zapis odbywa się do uporządkowanej struktury plików oraz same nazwy plików są zgodne z wymaganiami.

## Jak uruchomić aplikację:
1. cd Supervision3mISIe
2. pip install -r requirements.txt
3. python app/app2.py
4. Przejdź do http://127.0.0.1:8050/.
5. Enjoy:)
