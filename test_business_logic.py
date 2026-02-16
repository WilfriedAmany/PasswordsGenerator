"""
test_business_logic.py

This test suite validates the input validation rules defined in business_logic.validate_inputs().
It focuses on:
- Accepting only letters (a–z/A–Z, no accents or symbols) for word1 and word2
- Accepting only digits for number, with a length between 1 and 10
- Accepting only allowed special characters for special_char
- Ensuring the combined input length is at least 8 characters

Run with:
    pytest test_business_logic.py
Prerequisites:
    - Activate your virtual environment
    - pip install pytest
"""

import pytest
from business_logic import validate_inputs, allowed_special_chars


def test_valid_inputs():
    """
    Happy-path test:
    - Inputs strictly follow the rules
    - validate_inputs should return (True, concatenated_string)
    - concatenated_string must be at least 8 characters
    """
    result, value = validate_inputs("Alpha", "Beta", "1234", "@")
    assert result is True, "Expected validation to pass for valid inputs."
    assert isinstance(value, str), "Expected concatenated value to be a string."
    assert len(value) >= 8, "Concatenated input should be at least 8 characters."


def test_invalid_word1_accent():
    """
    Negative test:
    - word1 contains an accent (Rémy), which is not allowed
    - Expect (False, error_message) and the message to reference 'word1'
    """
    result, error = validate_inputs("Rémy", "Beta", "1234", "@")
    assert result is False, "Validation should fail for accented word1."
    assert "word1" in error, "Error message should indicate word1 is invalid."


def test_invalid_word2_symbol():
    """
    Negative test:
    - word2 contains a digit and a symbol (B3ta!), which violates the letters-only rule
    - Expect failure referencing word2
    """
    result, error = validate_inputs("Alpha", "B3ta!", "1234", "@")
    assert result is False, "Validation should fail when word2 has non-letter characters."
    assert "word2" in error, "Error message should indicate word2 is invalid."


def test_invalid_number_letters():
    """
    Negative test:
    - number contains letters (12ab)
    - Should fail because only digits are allowed
    """
    result, error = validate_inputs("Alpha", "Beta", "12ab", "@")
    assert result is False, "Validation should fail when number contains letters."
    assert "number" in error, "Error message should indicate number is invalid."


def test_invalid_number_length():
    """
    Negative test:
    - number is longer than 10 digits
    - Should fail due to length constraint
    """
    result, error = validate_inputs("Alpha", "Beta", "12345678901", "@")
    assert result is False, "Validation should fail for number longer than 10 digits."
    assert "number" in error, "Error message should indicate number length issue."


def test_invalid_special_char():
    """
    Negative test:
    - special_char is not in the allowed list (~)
    - Should fail and message should reference special_char constraint
    """
    result, error = validate_inputs("Alpha", "Beta", "1234", "~")
    assert result is False, "Validation should fail for disallowed special character."
    assert "special_char" in error, "Error message should indicate special_char is invalid."


def test_combined_input_too_short():
    """
    Negative test:
    - Inputs produce a concatenated string under 8 characters
    - Expect failure referring to minimum length requirement
    """
    result, error = validate_inputs("A", "B", "1", "@")
    assert result is False, "Validation should fail when combined input is too short."
    assert "at least 8 characters" in error, "Error message should indicate min length."


@pytest.mark.parametrize("char", allowed_special_chars)
def test_all_allowed_special_chars(char):
    """
    Parameterized test:
    - Iterates through each allowed special character
    - Ensures each passes validation when other inputs are valid
    - Also checks the chosen special_char appears in the concatenated output
    """
    result, value = validate_inputs("Alpha", "Beta", "1234", char)
    assert result is True, f"Expected validation to pass for allowed char: {char}"
    assert char in value, "Concatenated output should contain the chosen special character."

