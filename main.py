def add(a, b):
    return a + b

def rectangle_area(a, b):
    return a * b

def hypotenuse(a, b):
    return (a**2 + b**2)**0.5

def is_even(num):
    if num % 2 == 0:
        return True
    else:
        return False

def largest(a, b, c):
    lista = [a, b, c]
    najw = lista[0]
    for i in lista:
        if i > najw: najw = i
    return najw

def sum_to(n):
    suma = 0
    for x in range(n):
        suma += x+1
    return suma

def factorial(n):
    suma = 1
    if n != 0:
        for x in range(n, 0, -1):
            suma =+ suma * x
        return suma
    else:
        return 1

def count_digits(n):
    digits = 0
    if n > 0:
        while n > 0:
            n = n // 10
            digits += 1
    elif n < 0:
        n *= -1
        while n > 0:
            n = n // 10
            digits += 1
    return digits

def reverse_number(n):
    n = str(n)
    n = int(n[::-1])
    return n

def isPrime(n):
    if n == 2: return True
    elif n < 2: return False
    elif n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def sum_list(numbers):
    suma = 0
    for n in numbers:
        suma += n
    return suma

def largest_in_list(numbers):
    largest = numbers[0]
    for n in numbers:
        if n > largest:
            largest = n
    return largest

def count_occurrences(items, target):
    suma = 0
    for item in items:
        if item == target:
            suma += 1
    return suma

def common_elements(list1, list2):
    lista = []
    for i in list1:
        for j in list2:
            if i == j:
                lista.append(i)
    return lista

def distance_from_origin(point):
    return (point[0]**2 + point[1]**2)**0.5

def count_words(text):
    licznik = { }
    words = text.split()
    for x in words:
        if x in licznik:
            licznik[x] += 1
        else: licznik[x] = 1
    return licznik

def best_player(scores):
    best_score = next(iter(scores.values()))
    best_player = next(iter(scores.keys()))
    for i in scores:
        if scores[i] > best_score:
            best_score = scores[i]
            best_player = i
    return best_player

def inventory_value(inventory):
    suma = 0
    for i in inventory:
        suma += inventory[i]["price"] * inventory[i]["qty"]
    return suma


def low_stock(inventory, threshold):
    low = []
    for i in inventory:
        if inventory[i]["qty"] < threshold:
            low.append(i)
    return low

def check_winner(board):
    # kolumny
    for j in range(len(board[0])):
        a = []
        for i in range(len(board)):
            a.append(board[i][j])
        if len(set(a)) == 1:
            return a[0]

    # wiersze
    for wiersz in board:
        if len(set(wiersz)) == 1:
            return wiersz[0]

    # skosy
    g = []
    for i in range(len(board)):
        g.append(board[i][i])
    if len(set(g)) == 1:
        return g[0]

    h = []
    for i in range(len(board)):
        h.append(board[i][len(board) - 1 - i])
    if len(set(h)) == 1:
        return h[0]
    return "Draw"


print(check_winner(board = [
    ["x", "x", "x"],
    ["x", "o", "o"],
    ["o", "x", "x"]
]))
