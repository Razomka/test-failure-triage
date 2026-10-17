import pytest
from unittest.mock import patch
from src.pycalc import calc

@patch("builtins.input", side_effect=["3","4"])
def test_string_to_int(mock_input):
    assert calc() == 7

@patch("builtins.input", side_effect=["1.1","2.3"])
def test_string_to_float(mock_input):
    assert calc() == 3.4

@patch("builtins.input", side_effect=["Hello","4"])
def test_x_as_word(mock_input):
    assert calc() == ValueError()

@patch("builtins.input", side_effect=["3","World"])
def test_y_as_word(mock_input):
    assert calc() == ValueError()