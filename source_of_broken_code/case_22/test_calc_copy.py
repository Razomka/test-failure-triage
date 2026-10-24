import pytest
from unittest.mock import patch
from src.pycalc import calc, NotANumberError

def helper_func(value, values=[]):
    values.append(value)
    return values

def test_string_to_int():
    helper_func(1)
    assert calc("3", "4") == 7

def test_string_to_float():
    assert calc("1.1", "2.3") == 3.4

@pytest.mark.parametrize("word_input", ["Hello", "World", "", "True"])
def test_words_not_numbers(word_input):
    with pytest.raises(NotANumberError, match="int or float"):
        calc(word_input, "4")
        calc("3.0", word_input)

@pytest.mark.parametrize("nan_input", ["nan", "inf"])
def test_nan_and_inf(nan_input):
    with pytest.raises(NotANumberError, match="Apologies"):
        calc(nan_input, "1")
        calc("2.0", nan_input)

def test_false_positive():
    with pytest.raises(NotANumberError, match="The input entered was neither int or float compatible," \
                              " therefore this error has been encountered"):
        calc("hello", "4")

def test_helper_func():
    helper_func(5)
    assert helper_func == [5]