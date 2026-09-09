# Projekt: API do kółka i krzyżyka

Serwer HTTP w FastAPI, który trzyma stan jednej partii kółka i krzyżyka i
obsługuje ją przez trzy endpointy. Front (gotowy plik `tictactoe.html`) tylko
rysuje to, co dostanie w odpowiedzi — **cała logika gry siedzi na serwerze**.

Plansza to 3×3, pola numerowane od `0` do `8`, po kolei wierszami:

```
 0 | 1 | 2
---+---+---
 3 | 4 | 5
---+---+---
 6 | 7 | 8
```

Zaczyna gracz `"X"`. Gracze grają na przemian na tej samej planszy — serwer sam
wie, czyja jest kolej, klient tego nie przysyła.

---

## Uruchomienie

Wszystko w jednym pliku `server.py`.

```bash
pip install fastapi uvicorn
uvicorn server:app --port 8000 --reload
```

Serwer ma słuchać na `127.0.0.1:8000`. Dokumentacja endpointów generuje się sama
pod `http://127.0.0.1:8000/docs` — używaj jej do klikania po API w trakcie
pisania.

Ponieważ `tictactoe.html` otwierasz z dysku (`file://`), przeglądarka uzna go za
inne źródło niż serwer i zablokuje zapytania. Trzeba włączyć CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Stan gry

Serwer obsługuje **jedną** partię naraz — trzymaną w pamięci procesu, w zwykłej
zmiennej globalnej. Żadnej bazy danych, żadnych sesji, żadnych identyfikatorów
gier. Restart serwera kasuje partię i to jest w porządku.

Logikę gry trzymaj w osobnej klasie (`Game`), a funkcje endpointów niech tylko
ją wołają i zwracają wynik. Funkcja endpointu nie powinna sama sprawdzać, kto
wygrał.

---

## Struktura odpowiedzi

**Wszystkie trzy endpointy zwracają dokładnie ten sam kształt odpowiedzi.**
To jest najważniejsze wymaganie tego zadania — dzięki temu front ma jedną
funkcję rysującą i nie obchodzi go, skąd dane przyszły.

```json
{
  "board": ["X", "X", "X", "O", "O", null, null, null, null],
  "current": null,
  "winner": "X",
  "winning_line": [0, 1, 2],
  "draw": false,
  "finished": true
}
```

| Pole           | Typ                    | Znaczenie                                                        |
|----------------|------------------------|------------------------------------------------------------------|
| `board`        | lista 9 elementów      | zawartość pól: `"X"`, `"O"` albo `null` dla pustego              |
| `current`      | `"X"` / `"O"` / `null` | czyja kolej; `null` gdy gra się skończyła                        |
| `winner`       | `"X"` / `"O"` / `null` | zwycięzca; `null` gdy gra trwa albo jest remis                   |
| `winning_line` | lista 3 liczb / `null` | indeksy pól, które dały wygraną; `null` gdy nikt nie wygrał      |
| `draw`         | `true` / `false`       | czy plansza się zapełniła bez wygranej                           |
| `finished`     | `true` / `false`       | czy partia jest zakończona (wygrana **albo** remis)              |

Kilka rzeczy, które łatwo zrobić źle:

- `board` ma **zawsze** 9 elementów, także na pustej planszy. Nie skracaj listy,
  nie zwracaj `""` zamiast `null`.
- `finished` to nie to samo co `winner is not None` — remis też kończy grę.
- `current` po zakończonej partii to `null`, a nie symbol gracza, który miałby
  teoretycznie ruch.
- `winning_line` jest po to, żeby front podświetlił trzy pola. Bez tego musiałby
  sam liczyć, kto wygrał — czyli duplikować logikę serwera.

---

## Endpointy

### `GET /game`

Zwraca stan obecnej partii. Niczego nie zmienia — wywołany dziesięć razy pod
rząd zwraca dziesięć razy to samo.

Front woła to raz przy starcie, żeby po odświeżeniu strony pokazać planszę
w takim stanie, w jakim została.

Odpowiedź na świeżo uruchomionym serwerze:

```json
{
  "board": [null, null, null, null, null, null, null, null, null],
  "current": "X",
  "winner": null,
  "winning_line": null,
  "draw": false,
  "finished": false
}
```

### `POST /game`

Zaczyna nową partię: czyści planszę, kolej wraca na `"X"`, zwycięzca i remis się
zerują. Nie przyjmuje żadnego ciała zapytania.

Zwraca stan świeżej planszy — czyli to samo, co `GET /game` zaraz po nim.

Wywołanie na partii w trakcie po prostu ją kasuje. Nie pytaj o potwierdzenie,
nie zwracaj błędu.

### `POST /game/move`

Wykonuje ruch. Ciało zapytania:

```json
{ "index": 4 }
```

Symbolu gracza **nie** przysyłamy — serwer stawia symbol tego gracza, którego
jest kolej, i sam przełącza kolejkę na przeciwnika.

Po postawieniu symbolu serwer sprawdza, czy ten ruch wygrał partię, a jeśli nie
— czy plansza się zapełniła. Zwraca stan po ruchu, w tym samym formacie co
wyżej.

Serwer musi sprawdzić, czy ruch jest w ogóle dozwolony: czy `index` mieści się
w zakresie 0–8, czy pole jest wolne i czy partia jeszcze trwa.

---

## Błędy

Błędy zgłaszaj przez `HTTPException`, z sensownym komunikatem w `detail`:

```python
from fastapi import HTTPException

raise HTTPException(status_code=409, detail="Cell is already taken")
```

FastAPI zamieni to na odpowiedź:

```json
{ "detail": "Cell is already taken" }
```

| Sytuacja                          | Kod   |
|-----------------------------------|-------|
| pole jest już zajęte              | `409` |
| partia jest już zakończona        | `409` |
| `index` poza zakresem 0–8         | `422` |
| `index` nie jest liczbą całkowitą | `422` |

**Nieudany ruch nie może zmienić stanu gry.** Po odrzuconym zapytaniu plansza
wygląda tak samo jak przed nim i kolejka nadal należy do tego samego gracza.
Sprawdź kolejność w swoim kodzie: walidacja idzie **przed** postawieniem symbolu.

Nie zwracaj błędów jako `200` z polem `"error"` w środku. Kod HTTP jest od
mówienia, czy zapytanie się udało — front rozpoznaje błąd po nim, a nie po
zawartości odpowiedzi.

---

## Do zrobienia po kolei

1. Puste `server.py` z `app = FastAPI()` i CORS-em — sprawdź, czy `/docs` się
   otwiera.
2. Klasa `Game` ze stanem i metodą `reset()`. Do tego `GET /game` i `POST /game`
   — na tym etapie plansza jest zawsze pusta i to wystarczy.
3. `POST /game/move`, na razie bez sprawdzania wygranej: postaw symbol, przełącz
   kolejkę. Otwórz `tictactoe.html` — powinno już dać się klikać.
4. Wykrywanie wygranej i remisu, `winner`, `winning_line`, `draw`, `finished`.
5. Obsługa błędów: zajęte pole, ruch po końcu partii.

---

## Podpowiedzi

Osiem możliwych linii wygrywających wypisz raz, jako stałą — trzy wiersze, trzy
kolumny i dwie przekątne, każda jako trójka indeksów — i przelatuj je pętlą. Nie
pisz ośmiu `if`-ów.

Sprawdzając linię, uważaj na puste pola: trzy `None` obok siebie są sobie równe,
ale wygraną nie są.

Remis sprawdzaj **po** wygranej. Ruch zapełniający ostatnie pole może przecież
wygrywać, a wtedy to wygrana, nie remis.

Do testowania endpointów bez przeglądarki:

```bash
curl -X POST http://127.0.0.1:8000/game
curl -X POST http://127.0.0.1:8000/game/move \
  -H 'Content-Type: application/json' -d '{"index": 4}'
curl http://127.0.0.1:8000/game
```
