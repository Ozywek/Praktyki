
import pytest
import main as f

def test_add_adding(): #1
    assert f.add(1, 2) == 3

def test_rectangle_area_multiply(): #2
    assert f.rectangle_area(2,  6) == 12

def test_hypotenuse_incitement(): #3
    assert f.hypotenuse(3, 4) == 5

def test_is_even_for_even(): #4
    assert f.is_even(4) == True

def test_is_even_for_uneven(): #4
    assert f.is_even(5) == False

def test_largest_empty_values(): #5
    assert f.largest(0, 0, 0) == 0

def test_largest_values(): #5
    assert f.largest(-3, 32, -2) == 32

def test_sum_to_summing(): #6
    assert f.sum_to(3) == 6

def test_factorial_zero(): #7
    assert f.factorial(0) == 1

def test_factorial_summing(): #7
    assert f.factorial(3) == 6

def test_count_digits_negative_digit(): #8
    assert f.count_digits(-15) == 2

def test_count_digits_positive_digit(): #8
    assert f.count_digits(24) == 2

def test_reverse_number_reversing(): #9
    assert f.reverse_number(123) == 321

def test_isPrime_for_two(): #10
    assert f.isPrime(2) == True

def test_isPrime_smaller_than_two(): #10
    assert f.isPrime(-1) == False

def test_isPrime_even_number(): #10
    assert f.isPrime(4) == False

def test_isPrime_prime_number(): #10
    assert f.isPrime(7) == True

def test_isPrime_non_prime_number(): #10
    assert f.isPrime(9) == False

def test_sum_list_empty_list(): #11
    assert f.sum_list([]) == 0

def test_sum_list(): #11
    assert f.sum_list([1, 5, 6]) == 12

def test_largest_in_list(): #12
    assert f.largest_in_list([4, 8, 1]) == 8

def test_count_occurrences_no_target(): #13
    assert f.count_occurrences([2, 1, 4], 6) == 0

def test_count_occurrences(): #13
    assert f.count_occurrences([2, 3, 4, 3, 3, 3, 3, 1, 3, 4, 5, 6, 6], 3) == 6

def test_common_elements_no_common(): #14
    assert f.common_elements([2, 4] ,[1, 3]) == []

def test_common_elements(): #14
    assert f.common_elements([2, 4, 3, 1] ,[2, 4, 7, 9]) == [2, 4]

def test_distance_from_origin(): #15
    assert f.distance_from_origin([4, 3]) == 5

def test_count_words_empty(): #16
    assert f.count_words("") == {}

def test_count_words(): #16:
    assert f.count_words("dog dog cat") == {"dog": 2, "cat": 1}

def test_best_player(): #17
    assert f.best_player(scores = {
    "Adam": 15,
    "Bartek": 21,
    "Kasia": 18,
    "Ola": 25
}) == "Ola"

def test_inventory_value_for_empty_inventory(): #18
    assert f.inventory_value({}) == 0

def test_inventory_value_for_single_product(): #18
    assert f.inventory_value({"Bread": {"price": 1, "qty": 10}}) == 10

def test_low_stock_for_empty_inventory(): #19
    assert f.low_stock({}, 4) == []

def test_low_stock(): #19
    assert f.low_stock({"Bread": {"price": 1, "qty": 10}}, 15) == ["Bread"]

def test_check_winner_columns(): #20
    assert f.check_winner(board = [
    ["x", "x", "o"],
    ["x", "o", "o"],
    ["x", "o", "x"]
    ]) == "x"

def test_check_winner_rows(): #20
    assert f.check_winner(board = [
    ["x", "x", "o"],
    ["o", "o", "o"],
    ["x", "o", "x"]
    ]) == "o"

def test_check_winner_diagonal(): #20
    assert f.check_winner(board = [
    ["x", "x", "o"],
    ["x", "o", "o"],
    ["o", "o", "x"]
    ]) == "o"

def test_check_winner_draw(): #20
    assert f.check_winner(board = [
    ["x", "x", "o"],
    ["o", "x", "o"],
    ["x", "o", "x"]
    ]) == "Draw"
