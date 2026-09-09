import app
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    def making_move(self, ind):
        self.dict["board"][ind] = self.dict["current"]
        if self.dict["current"] == "X":
            self.dict["current"] = "O"
        else: self.dict["current"] = "X"

        return self.dict

game = Game()

class Move(BaseModel):
    index: int

@app.get("/game")
def root():
    return game.dict

@app.post("/game")
def reset():
    game.reset()
    return game.dict

@app.post("/game/move")
def make_move(move: Move):
    return game.making_move(move.index)
