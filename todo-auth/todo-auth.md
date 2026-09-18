# Projekt: logowanie do listy zadań (todo, część 2)

Rozszerzenie API z `todo-api.md` o konta użytkowników i sesje. Front
(`todo/index.html`) ma już formularz rejestracji i logowania, po starcie pyta
`GET /me` i w zależności od odpowiedzi pokazuje logowanie albo listę zadań.

Szkielet jest w `todo/server.py`. Poza tym, co było w części 1, dostajesz:

- `execute(sql, params=())` — helper przyjmuje teraz parametry zapytania,
  wartości od użytkownika przekazuj przez `?`, nigdy przez f-string
- `as_user` — zamienia wiersz z tabeli `users` na JSON, który zwraca API
- `hash_password` / `check_password` — bcrypt, hasła w bazie trzymasz tylko
  jako hash
- `new_session_token` — losowy token do cookie sesji

Wszystkie nowe endpointy mają docstring z opisem tego, co przyjmują i co
zwracają, a w ciele `raise NotImplementedError`.

---

## Uruchomienie

```bash
pip install fastapi uvicorn bcrypt
uvicorn server:app --port 8000 --reload
```

Uruchamiaj z katalogu `todo/`. Front pod `http://127.0.0.1:8000/`, dokumentacja
API pod `http://127.0.0.1:8000/docs`.

---

## 1. Schema bazy

Doszły dwa puste `CREATE TABLE IF NOT EXISTS`: `users` i `sessions`. Tak jak
w części 1, przejdź po docstringach i dla każdego pola zdecyduj o nazwie,
typie, `NOT NULL`, `DEFAULT` i kluczu głównym. Dodatkowo:

- `login` musi być unikalny — baza ma to pilnować (`UNIQUE`), nie kod
- `sessions` przechowuje token (to jest klucz główny, tekstowy) i id
  użytkownika, do którego należy — powiąż go z `users` przez `REFERENCES`
- `connect()` włącza `PRAGMA foreign_keys = ON`, więc klucze obce działają
- `tasks` dostaje właściciela — id użytkownika powiązane z `users`, bo od
  teraz każde zadanie należy do konkretnego konta (patrz punkt 4)

Jeśli masz `todo.db` z części 1, skasuj go — `CREATE TABLE IF NOT EXISTS` nie
przebuduje istniejących tabel.


## 2. Sesje

Po zalogowaniu serwer wystawia cookie `session_id` z losowym tokenem i
zapisuje ten token w tabeli `sessions`. Przy kolejnych requestach przeglądarka
sama dokleja cookie, a serwer po tokenie znajduje użytkownika. Front serwuje
ten sam serwer, więc nie ma CORS ani `credentials: "include"`.

W FastAPI potrzebujesz trzech rzeczy:

- **odczyt cookie** — parametr `session_id: str | None = Cookie(default=None)`
  w sygnaturze funkcji; nazwa parametru musi się zgadzać z nazwą cookie, a bez
  `default=None` brak cookie da 422 zamiast 401
- **ustawienie cookie** — parametr `response: Response` w sygnaturze i
  `response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax")`;
  zwracasz zwykły dict, FastAPI dokleja nagłówek `Set-Cookie`
- **skasowanie cookie** — `response.delete_cookie(SESSION_COOKIE)`


## 3. Endpointy

### `POST /register` — nowe konto

- zwaliduj body: `login` niepusty, przycięty, max 50 znaków; `password`
  min 8 znaków — reszta jak przy `title` w części 1, model Pydantic zrobi 422
- wstaw wiersz do `users` z hashem hasła z `hash_password`, nigdy z hasłem
  jawnym
- jeśli login jest zajęty, `INSERT` rzuci `sqlite3.IntegrityError` — złap go
  i zwróć `409` z detalem `"Login already taken"`
- załóż sesję: nowy token, wiersz w `sessions`, cookie w odpowiedzi
- zwróć użytkownika przez `as_user` ze statusem `201`

Zakładanie sesji powtarza się w `/login` — wynieś je do jednej funkcji.

### `POST /login` — logowanie

- znajdź użytkownika po `login`
- jeśli nie ma go w bazie albo `check_password` zwróci `False` — `401` z
  detalem `"Invalid login or password"`; jeden komunikat na oba przypadki,
  żeby nie zdradzać, które loginy istnieją
- załóż sesję tak samo jak przy rejestracji
- zwróć użytkownika przez `as_user`

### `GET /me` — kto jest zalogowany

- odczytaj cookie `session_id`
- jeśli go nie ma albo nie ma takiego tokenu w `sessions` — `401` z detalem
  `"Not logged in"`
- w przeciwnym razie znajdź użytkownika, do którego należy sesja (`JOIN` z
  `users`), i zwróć go przez `as_user`

### `POST /logout` — wylogowanie

- sprawdź sesję tak samo jak w `/me` — brak lub nieznany token to `401`
- usuń wiersz z `sessions` po tokenie
- skasuj cookie i zwróć `204` z pustym body

Sprawdzanie sesji powtarza się w obu endpointach — wynieś je do jednej funkcji.

## 4. Zabezpieczenie zadań

Endpointy z części 1 są otwarte: każdy może czytać i zmieniać wszystkie
zadania. Teraz wszystkie cztery (`GET /tasks`, `POST /tasks`,
`PATCH /tasks/{task_id}`, `DELETE /tasks/{task_id}`) mają wymagać zalogowania
i działać tylko na zadaniach zalogowanego użytkownika.

- **kto pyta** — na początku każdego z nich sprawdź sesję tak samo jak w
  `/me`; brak lub nieznany token to `401` z detalem `"Not logged in"`, zanim
  cokolwiek dotkniesz w bazie
- **`GET /tasks`** — zwróć tylko zadania, których właścicielem jest
  zalogowany użytkownik
- **`POST /tasks`** — zapisz nowe zadanie z id zalogowanego użytkownika jako
  właścicielem; id nie przychodzi w body, bierzesz je z sesji
- **`PATCH` i `DELETE`** — zadanie musi istnieć **i** należeć do zalogowanego
  użytkownika; cudze zadanie traktuj tak samo jak nieistniejące, czyli `404`
  z detalem `"Task not found"` — nie zdradzaj, że istnieje

Najprościej dopisać warunek na właściciela do każdego `WHERE`, obok warunku
na `id`. Wtedy jedno zapytanie załatwia i istnienie, i dostęp.

Sprawdź, że to działa: zarejestruj dwa konta, dodaj zadanie na pierwszym i
spróbuj je odhaczyć lub usunąć z drugiego — ma być `404`. Lista drugiego konta
ma być pusta.

---

## 5. Sprawdzenie

Pod `/docs` cookies nie zadziałają wygodnie, testuj z frontu albo curlem:

```bash
curl -i -c cookies.txt -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"login": "ann", "password": "password1"}'

curl -i -b cookies.txt http://127.0.0.1:8000/me

curl -i -b cookies.txt -c cookies.txt -X POST http://127.0.0.1:8000/logout

curl -i -b cookies.txt http://127.0.0.1:8000/me
```

Kolejno: `201` i nagłówek `Set-Cookie`, `200` z użytkownikiem, `204`, `401`.
