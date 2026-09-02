def largest_in_list(numbers):
    largest = numbers[0]
    for n in numbers:
        if n > largest:
            largest = n
    return largest



