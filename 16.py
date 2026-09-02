def count_words(text):
    licznik = { }
    words = text.split()
    for x in words:
        if x in licznik:
            licznik[x] += 1
        else: licznik[x] = 1
    return licznik



