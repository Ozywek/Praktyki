def count_digits(n):
    digits = 0
    while n > 0:
        n = n // 10
        digits += 1
    return digits
