"""Conformance tests for the tic-tac-toe API (see tic-tac-toe-api.md).

Start your server yourself, then point these tests at it:

    pytest test_api.py                                  # http://127.0.0.1:8000
    API_URL=http://127.0.0.1:9000 pytest test_api.py

The tests only speak HTTP - they do not care how or where the server runs.
Every test starts from a fresh game (POST /game).

Failure messages are in Polish on purpose: they are read by the interns.
"""
import json
import os
import urllib.error
import urllib.request
from textwrap import dedent

import pytest

BASE_URL = os.environ.get("API_URL", "http://127.0.0.1:8000").rstrip("/")

FIELDS = {"board", "current", "winner", "winning_line", "draw", "finished"}
EMPTY_BOARD = [None] * 9

WIN_TOP_ROW = [0, 3, 1, 4, 2]
WIN_ON_LAST_MOVE = [0, 2, 1, 3, 4, 6, 5, 7, 8]
DRAW = [0, 1, 2, 4, 3, 5, 7, 6, 8]


def request(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE_URL + path,
        method=method,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        payload = error.read()
        try:
            return error.code, json.loads(payload)
        except json.JSONDecodeError:
            return error.code, payload.decode(errors="replace")


def board_art(board, indent="    "):
    if not isinstance(board, list) or len(board) != 9:
        return f"{indent}(board nie jest listą 9 pól: {board!r})"
    cells = [" ·" if c is None else f" {c}" for c in board]
    return "\n".join(indent + " ".join(cells[i:i + 3]) for i in (0, 3, 6))


def problem(what, *, hint=None, moves=None, state=None, before=None, after=None):
    """Buduje komunikat błędu: co jest źle, dlaczego, i co serwer zwrócił."""
    lines = [what]

    if hint:
        lines += ["", *(f"  {line}" for line in dedent(hint).strip().splitlines())]

    if moves:
        lines += ["", f"  ruchy: {' → '.join(str(m) for m in moves)}"]

    if before is not None and after is not None:
        lines += ["", "  przed:", board_art(before.get("board"), "      ")]
        lines += ["", "  po:", board_art(after.get("board"), "      ")]
        changed = [
            f"    {f}: {before.get(f)!r} → {after.get(f)!r}"
            for f in sorted(FIELDS - {"board"})
            if before.get(f) != after.get(f)
        ]
        if changed:
            lines += ["", "  zmienione pola:", *changed]

    if state is not None:
        if isinstance(state, dict) and "board" in state:
            lines += ["", "  plansza:", board_art(state["board"], "      ")]
            lines += ["", "  serwer zwrócił:"]
            lines += [
                f"    {field:<13}= {state.get(field, '<brak pola>')!r}"
                for field in ("current", "winner", "winning_line", "draw", "finished")
            ]
        else:
            lines += ["", f"  serwer zwrócił: {state!r}"]

    return "\n".join(lines) + "\n"


class Client:
    def get(self):
        return request("GET", "/game")[1]

    def reset(self):
        return request("POST", "/game")[1]

    def move(self, index):
        return request("POST", "/game/move", {"index": index})

    def play(self, indexes):
        for n, index in enumerate(indexes, 1):
            status, state = self.move(index)
            assert status == 200, problem(
                f"Ruch nr {n} (pole {index}) został odrzucony kodem {status}, "
                f"a jest całkowicie poprawny.",
                moves=indexes,
                state=state,
            )
        return state


@pytest.fixture(scope="session")
def server():
    client = Client()
    try:
        client.get()
    except urllib.error.URLError as error:
        pytest.exit(f"Brak serwera pod {BASE_URL} ({error.reason}). Odpal go najpierw.", 1)
    return client


@pytest.fixture(autouse=True)
def fresh_game(server):
    server.reset()
    return server


def test_server_answers(server):
    state = server.get()
    assert state["board"] == EMPTY_BOARD, problem(
        "Po POST /game plansza nie jest pusta.",
        state=state,
    )


def test_fresh_game_state(server):
    state = server.get()
    expected = {
        "board": EMPTY_BOARD,
        "current": "X",
        "winner": None,
        "winning_line": None,
        "draw": False,
        "finished": False,
    }
    wrong = [
        f"{field}: jest {state.get(field)!r}, powinno być {want!r}"
        for field, want in expected.items()
        if state.get(field) != want
    ]
    assert not wrong, problem(
        f"Świeża partia ma {len(wrong)} złych pól.",
        hint="\n".join(wrong),
        state=state,
    )


def test_every_endpoint_returns_the_same_six_fields(server):
    for name, state in [
        ("GET /game", server.get()),
        ("POST /game", server.reset()),
        ("POST /game/move", server.move(4)[1]),
    ]:
        missing = sorted(FIELDS - set(state))
        extra = sorted(set(state) - FIELDS)
        assert not missing and not extra, problem(
            f"{name} zwraca inny zestaw pól niż pozostałe endpointy.",
            hint=f"""
                Wszystkie trzy endpointy muszą zwracać dokładnie te same sześć pól -
                dzięki temu front ma jedną funkcję rysującą.
                brakuje:    {missing or 'nic'}
                nadmiarowe: {extra or 'nic'}
            """,
            state=state,
        )


def test_board_is_always_nine_cells(server):
    state = server.get()
    assert len(state["board"]) == 9, problem(
        f"Pusta plansza ma {len(state['board'])} pól zamiast 9.",
        hint="Puste pole to null, a nie brak elementu w liście.",
        state=state,
    )
    server.play([4, 0])
    state = server.get()
    assert len(state["board"]) == 9, problem(
        f"Po dwóch ruchach plansza ma {len(state['board'])} pól zamiast 9.",
        state=state,
    )


def test_get_does_not_change_state(server):
    server.play([4])
    first, second = server.get(), server.get()
    assert first == second, problem(
        "Dwa kolejne GET /game zwróciły różne rzeczy.",
        hint="GET ma tylko czytać stan, niczego nie zmieniać.",
        before=first,
        after=second,
    )


def test_post_game_resets_a_started_game(server):
    server.play([0, 1, 2])
    returned = server.reset()
    state = server.get()
    assert returned == state, problem(
        "POST /game zwrócił co innego, niż pokazuje GET /game zaraz po nim.",
        hint="Oba endpointy opisują ten sam stan, więc muszą zwrócić to samo.",
        before=returned,
        after=state,
    )
    assert state["board"] == EMPTY_BOARD, problem(
        "POST /game na partii w trakcie nie wyczyścił planszy.",
        state=state,
    )
    assert state["current"] == "X", problem(
        f"Po POST /game kolej ma wrócić na 'X', a jest {state['current']!r}.",
        state=state,
    )


def test_players_alternate(server):
    state = server.move(0)[1]
    assert state["current"] == "O", problem(
        f"Po pierwszym ruchu X kolej powinna przejść na 'O', "
        f"a serwer mówi {state['current']!r}.",
        moves=[0],
        state=state,
    )
    state = server.move(4)[1]
    assert state["board"][4] == "O", problem(
        f"Drugi ruch powinien postawić 'O' na polu 4, a stoi tam {state['board'][4]!r}.",
        hint="Symbol bierzesz z 'current' - klient go nie przysyła.",
        moves=[0, 4],
        state=state,
    )
    assert state["current"] == "X", problem(
        f"Po ruchu O kolej powinna wrócić na 'X', a jest {state['current']!r}.",
        moves=[0, 4],
        state=state,
    )


def test_win(server):
    state = server.play(WIN_TOP_ROW)
    assert state["winner"] == "X", problem(
        f"X zajął cały górny wiersz (pola 0, 1, 2), a serwer mówi "
        f"winner={state['winner']!r}.",
        moves=WIN_TOP_ROW,
        state=state,
    )
    assert sorted(state["winning_line"] or []) == [0, 1, 2], problem(
        f"winning_line powinno być [0, 1, 2], a jest {state['winning_line']!r}.",
        hint="Front podświetla po tym polu wygrywającą linię.",
        moves=WIN_TOP_ROW,
        state=state,
    )
    assert state["finished"] is True, problem(
        f"Partia jest wygrana, więc finished ma być True, a jest {state['finished']!r}.",
        moves=WIN_TOP_ROW,
        state=state,
    )
    assert state["draw"] is False, problem(
        f"Wygrana to nie remis - draw ma być False, a jest {state['draw']!r}.",
        moves=WIN_TOP_ROW,
        state=state,
    )


WIN_ON_LAST_MOVE_HINT = """
    Ostatni ruch zapełnił planszę I JEDNOCZEŚNIE wygrał przekątną 0-4-8.
    To jest wygrana, nie remis.
    Remis sprawdzaj PO wygranej i tylko wtedy, gdy wygranej nie było.
"""


def test_win_on_the_last_move_is_a_win_not_a_draw(server):
    state = server.play(WIN_ON_LAST_MOVE)
    assert state["winner"] == "X", problem(
        f"X wygrał ostatnim ruchem, a serwer mówi winner={state['winner']!r}.",
        hint=WIN_ON_LAST_MOVE_HINT,
        moves=WIN_ON_LAST_MOVE,
        state=state,
    )
    assert state["draw"] is False, problem(
        f"draw ma być False, a jest {state['draw']!r}.",
        hint=WIN_ON_LAST_MOVE_HINT,
        moves=WIN_ON_LAST_MOVE,
        state=state,
    )
    assert sorted(state["winning_line"] or []) == [0, 4, 8], problem(
        f"winning_line powinno być [0, 4, 8], a jest {state['winning_line']!r}.",
        hint=WIN_ON_LAST_MOVE_HINT,
        moves=WIN_ON_LAST_MOVE,
        state=state,
    )
    assert state["finished"] is True, problem(
        f"finished ma być True, a jest {state['finished']!r}.",
        moves=WIN_ON_LAST_MOVE,
        state=state,
    )


def test_current_is_null_after_a_win(server):
    state = server.play(WIN_TOP_ROW)
    assert state["current"] is None, problem(
        f"Partia jest wygrana, więc current ma być null, a jest {state['current']!r}.",
        hint=f"""
            Na skończonej partii nie ma czyjej kolei - front pokazałby
            „kolej gracza {state['current']}" na planszy, na której nie da się zagrać.
            Kolejkę przełączaj tylko wtedy, gdy gra toczy się dalej.
        """,
        moves=WIN_TOP_ROW,
        state=state,
    )


def test_draw(server):
    state = server.play(DRAW)
    assert state["draw"] is True, problem(
        f"Plansza zapełniła się bez wygranej, więc draw ma być True, "
        f"a jest {state['draw']!r}.",
        moves=DRAW,
        state=state,
    )
    assert state["winner"] is None, problem(
        f"W remisie nie ma zwycięzcy - winner ma być null, a jest {state['winner']!r}.",
        moves=DRAW,
        state=state,
    )
    assert state["winning_line"] is None, problem(
        f"W remisie nie ma wygrywającej linii - winning_line ma być null, "
        f"a jest {state['winning_line']!r}.",
        moves=DRAW,
        state=state,
    )
    assert state["finished"] is True, problem(
        f"Remis też kończy partię, więc finished ma być True, "
        f"a jest {state['finished']!r}.",
        hint="finished to nie to samo co 'winner is not None'.",
        moves=DRAW,
        state=state,
    )


def test_current_is_null_after_a_draw(server):
    state = server.play(DRAW)
    assert state["current"] is None, problem(
        f"Po remisie current ma być null, a jest {state['current']!r}.",
        hint="Partia jest skończona, więc nie ma czyjej kolei.",
        moves=DRAW,
        state=state,
    )


def test_move_after_a_finished_game_is_409(server):
    server.play(WIN_TOP_ROW)
    status, body = server.move(5)
    assert status == 409, problem(
        f"Ruch na skończonej partii zwrócił {status}, a ma zwrócić 409.",
        hint="Zanim postawisz symbol, sprawdź czy partia jeszcze trwa.",
        moves=WIN_TOP_ROW + [5],
        state=body,
    )


def test_move_after_a_finished_game_does_not_touch_the_board(server):
    before = server.play(WIN_TOP_ROW)
    server.move(5)
    after = server.get()
    assert after["board"] == before["board"], problem(
        "Odrzucony ruch po końcu partii zmienił planszę.",
        hint="Nieudany ruch nie może zmieniać stanu gry.",
        before=before,
        after=after,
    )


def test_taken_cell_is_409(server):
    server.play([4])
    status, body = server.move(4)
    assert status == 409, problem(
        f"Ruch na zajęte pole 4 zwrócił {status}, a ma zwrócić 409.",
        moves=[4, 4],
        state=body,
    )


def test_rejected_move_changes_nothing(server):
    before = server.play([0])
    status, _ = server.move(0)
    assert status == 409, problem(
        f"Ruch na zajęte pole 0 zwrócił {status}, a ma zwrócić 409.",
        state=before,
    )
    after = server.get()
    assert after == before, problem(
        "Odrzucony ruch zmienił stan gry.",
        hint="""
            Po odrzuconym zapytaniu plansza ma wyglądać tak samo jak przed nim,
            a kolejka ma należeć do tego samego gracza.
            Walidacja idzie PRZED postawieniem symbolu i przed zmianą kolejki.
        """,
        before=before,
        after=after,
    )


@pytest.mark.parametrize("index", [-1, 9, 100])
def test_index_out_of_range_is_422(server, index):
    status, body = server.move(index)
    assert status == 422, problem(
        f"index={index} jest poza planszą, a serwer zwrócił {status} zamiast 422.",
        hint="Pola są numerowane od 0 do 8.",
        state=body,
    )


@pytest.mark.parametrize("index", ["abc", None, 1.5, [4]])
def test_index_that_is_not_an_int_is_422(server, index):
    status, body = server.move(index)
    assert status == 422, problem(
        f"index={index!r} nie jest liczbą całkowitą, a serwer zwrócił {status} "
        f"zamiast 422.",
        state=body,
    )


def test_invalid_move_does_not_end_the_game(server):
    server.move(42)
    state = server.get()
    assert state["current"] == "X" and state["finished"] is False, problem(
        "Odrzucony ruch (index=42) popsuł stan gry.",
        hint="""
            Powinno być tak, jakby tego zapytania w ogóle nie było:
            kolej nadal 'X', finished nadal False.
        """,
        moves=[42],
        state=state,
    )
