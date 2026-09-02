def factorial(n):
    suma = 1
    if n != 0:
        for x in range(n, 0, -1):
            suma =+ suma * x
        return suma
    else:
        return 1


