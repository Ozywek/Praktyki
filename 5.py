def largest(a, b, c):
    lista = [a, b, c]
    najw = lista[0]
    for i in lista:
        if i > najw: najw = i
    return najw
