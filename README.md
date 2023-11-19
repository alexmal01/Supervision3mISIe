# Supervision3mISIe

## Moduły

### Scraper
Moduł składa się z 2 submodułów. Napisany przy wykorzustaniu biblioteki Beautiful Soup 4 w Pythonie. 

#### Pobieranie linków
Funkcja pobierania linków pracuje wielokątkowo (domyślnie jest to 6 linków per wątek, czyli w przypadku zadania potrzeba 9 wątków).
Przyjmuje listę linków. Tworzy pliki JSON zawierające:
 * `klucz` - url
 * `wartość` - true/false w zależności czy dana strona została odwiedziona
Wątki odwiedzają kolejne nieodwiedzone podstrony danej wejściowej domeny z listy. Każda wejściowa domena posiada timeout (domyślnie 30 minut), który ogranicza sytuacje wolnego połączenia do strony.

#### Pobieranie PDFów
Za pomocą słów kluczowych w linkach pobierane są odpowiednie PDFy z plikami SFCR oraz z audytami. Zapis odbywa się do uporządkowanej struktury plików oraz same nazwy plików są zgodne z wymaganiami.

