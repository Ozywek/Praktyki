def largest_in_list(numbers):
    largest = 0
    for n in numbers:
        if n > largest:
            largest = n
    return largest


