# Projekt: API do listy zadań (todo)

Serwer HTTP w FastAPI z bazą SQLite, który trzyma listę zadań i obsługuje ją
przez cztery endpointy. Gotowy front (`todo/index.html`) serwuje sam serwer pod
`/`, więc CORS nie jest potrzebny.

Szkielet jest w `todo/server.py` — połączenie z bazą, helper `execute` i
`as_task` są już napisane. Każdy endpoint ma docstring z opisem tego, co
przyjmuje i co zwraca, a w ciele `raise NotImplementedError` — to jest do
uzupełnienia.

---

## Uruchomienie

```bash
pip install fastapi uvicorn
uvicorn server:app --port 8000 --reload
```

Uruchamiaj z katalogu `todo/`. Front otwierasz pod `http://127.0.0.1:8000/`,
dokumentacja API generuje się sama pod `http://127.0.0.1:8000/docs`.

---

## 1. Schema bazy

`CREATE TABLE IF NOT EXISTS tasks` (na górze pliku) jest pusty — schemę
projektujesz sam. Przejdź po docstringach endpointów, wypisz, jakie pola API w
ogóle przechowuje, i dla **każdego** z nich zdecyduj:

- jak się nazywa (tak samo jak w JSON-ie, który zwraca API)
- jaki ma typ w SQLite (uwaga: SQLite nie ma typu `bool`)
- czy jest wymagane (`NOT NULL`)
- czy ma wartość domyślną (`DEFAULT`) — i jaką
- czy jest kluczem głównym i czy baza ma je nadawać sama

Plik bazy tworzy się sam przy starcie serwera. Jeśli zmienisz schemę po
pierwszym uruchomieniu, skasuj `todo.db` i odpal serwer jeszcze raz —
`CREATE TABLE IF NOT EXISTS` nie przebuduje istniejącej tabeli.


## 2. Endpointy

### `GET /` — front

- zwróć `FileResponse` z `index.html`

### `GET /tasks` — lista zadań

- pobierz wszystkie zadania, posortowane: najpierw niezrobione, potem od
  najnowszego
- zwróć listę zadań przepuszczonych przez `as_task`

### `POST /tasks` — nowe zadanie

- wstaw nowy wiersz z `title` z body i `done = 0`
- zwróć utworzone zadanie ze statusem `201`

### `PATCH /tasks/{task_id}` — odhaczenie zadania

- ustaw `done` na wartość z body (pamiętaj o konwersji `bool` → `0`/`1`)
- jeśli zadanie o takim `id` nie istnieje — `404` z detalem `"Task not found"`
- w przeciwnym razie zwróć zaktualizowane zadanie

### `DELETE /tasks/{task_id}` — usunięcie zadania

- usuń wiersz o danym `id`
- jeśli nie było takiego zadania — `404` z detalem `"Task not found"`
- w przeciwnym razie status `204` i puste body

---

