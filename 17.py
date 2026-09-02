def best_player(scores):
    best_score = next(iter(scores.values()))
    best_player = next(iter(scores.keys()))
    for i in scores:
        if scores[i] > best_score:
            best_score = scores[i]
            best_player = i
    return best_player

