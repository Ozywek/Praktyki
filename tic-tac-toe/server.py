import app
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Move(BaseModel):
    index: int

class Game:
    dict = {
        "board": [None, None, None, None, None, None, None, None, None],
        "current": "X",
        "winner": None,
        "winning_line": None,
        "draw": False,
        "finished": False
    }

    def reset(self):
        self.dict = {
        "board": [None, None, None, None, None, None, None, None, None],
        "current": "X",
        "winner": None,
        "winning_line": None,
        "draw": False,
        "finished": False
    }
    def check_winner(self):
        winning = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6)
        ]
        for a, b, c in winning:
            if self.dict["board"][a] == self.dict["board"][b] == self.dict["board"][c] and self.dict["board"][a] != None:
                return [a, b, c]
        return False

    def check_draw(self):
        if not None in self.dict["board"]:
            return True
        else:
            return False

    def one_move(self, ind):
        self.dict["board"][ind] = self.dict["current"]

        if self.check_draw() == False:
            if (a := self.check_winner()) == False:
            # if self.check_winner() == False:
                if self.dict["current"] == "X":
                    self.dict["current"] = "O"
                else:
                    self.dict["current"] = "X"
            else:
                self.dict["winning_line"] = a
                self.dict["winner"] = self.dict["current"]
                self.dict["finished"] = True
        else:
            self.dict["draw"] = True
            self.dict["finished"] = True

        return self.dict

game = Game()

@app.get("/game")
def root():
    return game.dict

@app.post("/game")
def reset():
    game.reset()
    return game.dict

@app.post("/game/move")
def make_move(move: Move):
    # if not isinstance(move.index , int):
    #     raise HTTPException(status_code=422, detail="Index is not an integer")
    if move.index > 8:
        raise HTTPException(status_code=422, detail="Index out of range")
    elif game.dict["finished"]:
        raise HTTPException(status_code=409, detail="Game already ended")
    elif game.dict["board"][move.index] != None:
        raise HTTPException(status_code=409, detail="Cell is already taken")


    return game.one_move(move.index)



