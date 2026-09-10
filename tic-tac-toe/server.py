from fastapi import FastAPI
from typing import Annotated
from pydantic import BaseModel, Field
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
  index: Annotated[int, Field(ge=0, le=8)]

class Game:
    dict = {
        "board": [None, None, None, None, None, None, None, None, None],
        "current": "X",
        "winner": None,
        "winning_line": None,
        "draw": False,
        "finished": False,
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
        return self.dict
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

        if (a := self.check_winner()) == False:
            if self.check_draw() == False:
                if self.dict["current"] == "X":
                    self.dict["current"] = "O"
                else:
                    self.dict["current"] = "X"
            else:
                self.dict["draw"] = True
                self.dict["finished"] = True
                self.dict["current"] = None
        else:
            self.dict["winning_line"] = a
            self.dict["winner"] = self.dict["current"]
            self.dict["finished"] = True
            self.dict["current"] = None
        return self.dict

    def is_finished(self):
        if self.dict["finished"]:
            return  True
        else:
            return False

    def is_taken(self, ind):
        if self.dict["board"][ind] != None:
            return True
        else: return False


    def get_dict(self):
            return self.dict


game = Game()

@app.get("/game")
def root():
    return game.get_dict()

@app.post("/game")
def reset():
    return game.reset()

@app.post("/game/move")
def make_move(move: Move):

    if game.is_finished():
        raise HTTPException(status_code=409, detail="Game already ended")
    elif game.is_taken(move.index):
        raise HTTPException(status_code=409, detail="Cell is already taken")

    return game.one_move(move.index)



