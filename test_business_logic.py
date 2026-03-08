"""
test_business_logic.py

Extended test suite covering:
- validate_inputs: input validation rules
- extract_and_split: fragment extraction and string splitting
- build_final_list: fragment merging and deduplication
- generate_password: password construction rules, length correctness, edge cases
- generate_passwords: full orchestration flow, ValueError on invalid input

Run with:
    pytest test_business_logic.py
Prerequisites:
    - Activate your virtual environment
    - pip install pytest
"""

import pytest
from business_logic import (
    validate_inputs,
    extract_and_split,
    build_final_list,
    generate_password,
    generate_passwords,
    allowed_special_chars,
)


# ─── validate_inputs ──────────────────────────────────────────────────────────

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
    - Each individual input passes its own rule, but the combined string is under 8 characters
      (word1="ab" + word2="cd" + number="1" + special_char="@" → "abcd1@" = 6 chars)
    - Expect failure referring to minimum length requirement
    """
    result, error = validate_inputs("ab", "cd", "1", "@")
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


# ─── extract_and_split ────────────────────────────────────────────────────────

def test_extract_and_split_structure():
    """Verify the shape and content of each extracted fragment list.
    Words are passed in lowercase, mirroring the normalization that
    generate_passwords applies before calling extract_and_split."""
    _, concat = validate_inputs("Alpha", "Beta", "1234", "@")
    first_last, two_first, three_first, tertil, quartil, quintil = extract_and_split("alpha", "beta", concat)

    assert first_last == ["aa", "ba"]
    assert two_first == ["al", "be"]
    assert three_first == ["alp", "bet"]
    assert len(tertil) == 3
    assert len(quartil) == 4
    assert len(quintil) == 5


def test_extract_and_split_tertil_reassembly():
    """Joining all tertile parts must reconstruct the full concatenated string."""
    _, concat = validate_inputs("Alpha", "Beta", "1234", "@")
    _, _, _, tertil, _, _ = extract_and_split("Alpha", "Beta", concat)
    assert "".join(tertil) == concat


def test_extract_and_split_quartil_reassembly():
    """Joining all quartile parts must reconstruct the full concatenated string."""
    _, concat = validate_inputs("Alpha", "Beta", "1234", "@")
    _, _, _, _, quartil, _ = extract_and_split("Alpha", "Beta", concat)
    assert "".join(quartil) == concat


def test_extract_and_split_quintil_types():
    """All quintile parts must be strings."""
    _, concat = validate_inputs("Hello", "World", "9999", "!")
    _, _, _, _, _, quintil = extract_and_split("Hello", "World", concat)
    assert len(quintil) == 5
    assert all(isinstance(p, str) for p in quintil)


# ─── build_final_list ─────────────────────────────────────────────────────────

def _fragments(word1="Alpha", word2="Beta", number="1234", char="@"):
    """Helper: returns all fragment lists for given inputs.
    Lowercases word1/word2 before extraction to mirror generate_passwords."""
    _, concat = validate_inputs(word1, word2, number, char)
    return extract_and_split(word1.lower(), word2.lower(), concat)


def test_build_final_list_contains_original_inputs():
    """The final list must contain all four inputs (word1/word2 lowercased,
    as generate_passwords normalizes them before building the pool)."""
    first_last, two_first, three_first, tertil, quartil, quintil = _fragments()
    result = build_final_list("alpha", "beta", "1234", "@",
                              first_last, two_first, three_first,
                              tertil, quartil, quintil)
    assert "alpha" in result
    assert "beta" in result
    assert "1234" in result
    assert "@" in result


def test_build_final_list_no_duplicates():
    """The final list must not contain duplicate elements."""
    first_last, two_first, three_first, tertil, quartil, quintil = _fragments()
    result = build_final_list("Alpha", "Beta", "1234", "@",
                              first_last, two_first, three_first,
                              tertil, quartil, quintil)
    assert len(result) == len(set(result))


def test_build_final_list_returns_non_empty_list():
    """The final list must be a non-empty list."""
    first_last, two_first, three_first, tertil, quartil, quintil = _fragments()
    result = build_final_list("Alpha", "Beta", "1234", "@",
                              first_last, two_first, three_first,
                              tertil, quartil, quintil)
    assert isinstance(result, list)
    assert len(result) > 0


# ─── generate_password ────────────────────────────────────────────────────────

def _make_components(word1="Alpha", word2="Beta", number="1234", char="@"):
    """Helper: returns (finale_list, tertil, quartil, number, char)."""
    first_last, two_first, three_first, tertil, quartil, quintil = _fragments(word1, word2, number, char)
    finale = build_final_list(word1, word2, number, char,
                              first_last, two_first, three_first,
                              tertil, quartil, quintil)
    return finale, tertil, quartil, number, char


@pytest.mark.parametrize("target_length", [8, 12, 14])
def test_generate_password_correct_length(target_length):
    """Generated password must have exactly the requested length."""
    finale, _, quartil, number, char = _make_components()
    pwd = generate_password(quartil, finale, target_length, number, char)
    assert len(pwd) == target_length, f"Expected length {target_length}, got {len(pwd)}"


def test_generate_password_contains_number():
    """Generated password must always include the numeric input (or its effective prefix)."""
    finale, _, quartil, number, char = _make_components()
    for _ in range(10):
        pwd = generate_password(quartil, finale, 12, number, char)
        assert number in pwd, f"Number '{number}' not found in '{pwd}'"


def test_generate_password_contains_special_char():
    """Generated password must always include the special character."""
    finale, _, quartil, number, char = _make_components()
    for _ in range(10):
        pwd = generate_password(quartil, finale, 12, number, char)
        assert char in pwd, f"Special char '{char}' not found in '{pwd}'"


def test_generate_password_has_at_least_one_uppercase():
    """
    The capitalisation step guarantees at least 1 uppercase letter.
    Since word1/word2 are normalized to lowercase before fragment extraction,
    all uppercase letters in the password come exclusively from the index-based
    capitalization step (1–2 random positions).
    """
    finale, _, quartil, number, char = _make_components()
    for _ in range(20):
        pwd = generate_password(quartil, finale, 14, number, char)
        assert any(c.isupper() for c in pwd), f"No uppercase letter found in '{pwd}'"


def test_generate_password_returns_string():
    """Return type must be str."""
    finale, _, quartil, number, char = _make_components()
    pwd = generate_password(quartil, finale, 8, number, char)
    assert isinstance(pwd, str)


# ─── generate_password — edge cases: long number (len >= target_length) ───────

def test_generate_password_long_number_correct_length():
    """
    When len(number) >= target_length (e.g. 8-digit number, target=8), the password
    must still have exactly target_length characters — the bug that caused the
    number injection to overflow the target length.
    """
    finale, _, quartil, number, char = _make_components("Alpha", "Beta", "12345678", "@")
    pwd = generate_password(quartil, finale, 8, number, char)
    assert len(pwd) == 8, f"Expected length 8, got {len(pwd)}"
    assert char in pwd, f"Special char '{char}' missing from '{pwd}'"


def test_generate_password_max_number_correct_length():
    """
    Edge case: 10-digit number (maximum allowed) with target_length=8 and target_length=12.
    The password must remain at the correct length in both cases.
    """
    finale, tertil, quartil, number, char = _make_components("Alpha", "Beta", "1234567890", "@")
    for start_list, target in [(quartil, 8), (tertil, 12)]:
        pwd = generate_password(start_list, finale, target, number, char)
        assert len(pwd) == target, f"Expected length {target}, got {len(pwd)}"
        assert char in pwd, f"Special char '{char}' missing from '{pwd}'"


def test_generate_password_clamped_number_prefix_in_password():
    """
    When len(number) >= target_length (e.g. 8-digit number with target=8),
    effective_number = number[:target_length - 1] must appear in the password.
    The full number may not fit, but its clamped prefix always must.
    """
    finale, _, quartil, number, char = _make_components("Alpha", "Beta", "12345678", "@")
    effective_number = number[:8 - 1]  # "1234567"
    for _ in range(10):
        pwd = generate_password(quartil, finale, 8, number, char)
        assert effective_number in pwd, (
            f"Effective number '{effective_number}' not found in '{pwd}'"
        )


def test_generate_passwords_long_number_all_lengths_correct():
    """
    Full flow with a 10-digit number must return 3 passwords of lengths 8, 12, 14.
    Covers the end-to-end fix for the number-clamping bug.
    """
    pw1, pw2, pw3 = generate_passwords("Alpha", "Beta", "1234567890", "@")
    assert len(pw1) == 8,  f"Expected pw1 length 8, got {len(pw1)}"
    assert len(pw2) == 12, f"Expected pw2 length 12, got {len(pw2)}"
    assert len(pw3) == 14, f"Expected pw3 length 14, got {len(pw3)}"


# ─── generate_passwords (full flow) ──────────────────────────────────────────

def test_generate_passwords_returns_three():
    """Full flow must return a tuple of exactly 3 passwords."""
    result = generate_passwords("Alpha", "Beta", "1234", "@")
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_generate_passwords_all_strings():
    """All 3 generated passwords must be strings."""
    pw1, pw2, pw3 = generate_passwords("Alpha", "Beta", "1234", "@")
    assert all(isinstance(p, str) for p in [pw1, pw2, pw3])


def test_generate_passwords_correct_lengths():
    """Passwords must have lengths 8, 12, and 14 respectively."""
    pw1, pw2, pw3 = generate_passwords("Alpha", "Beta", "1234", "@")
    assert len(pw1) == 8
    assert len(pw2) == 12
    assert len(pw3) == 14


def test_generate_passwords_invalid_inputs_raises_value_error():
    """
    Invalid inputs must cause generate_passwords to raise ValueError.
    The error message must reference the failing field.
    """
    with pytest.raises(ValueError, match="word1"):
        generate_passwords("Rémy", "Beta", "1234", "@")


def test_generate_passwords_invalid_number_raises_value_error():
    """Invalid number must raise ValueError referencing 'number'."""
    with pytest.raises(ValueError, match="number"):
        generate_passwords("Alpha", "Beta", "abc", "@")


def test_generate_passwords_invalid_special_char_raises_value_error():
    """Disallowed special character must raise ValueError referencing 'special_char'."""
    with pytest.raises(ValueError, match="special_char"):
        generate_passwords("Alpha", "Beta", "1234", "~")


def test_generate_passwords_all_contain_special_char():
    """All 3 passwords must contain the chosen special character."""
    for char in allowed_special_chars:
        pw1, pw2, pw3 = generate_passwords("Alpha", "Beta", "1234", char)
        for pwd in [pw1, pw2, pw3]:
            assert char in pwd, f"Special char '{char}' missing in '{pwd}'"


def test_generate_passwords_all_contain_number():
    """All 3 passwords must contain the numeric input."""
    pw1, pw2, pw3 = generate_passwords("Alpha", "Beta", "42", "!")
    for pwd in [pw1, pw2, pw3]:
        assert "42" in pwd, f"Number '42' missing in '{pwd}'"


@pytest.mark.parametrize("word1,word2,number,char", [
    ("Hello", "World", "2024", "@"),
    ("Python", "Code", "99", "!"),
    ("Secure", "Pass", "1234567", "#"),
])
def test_generate_passwords_parametrized(word1, word2, number, char):
    """Parametrized happy-path: verify lengths and types for various inputs."""
    result = generate_passwords(word1, word2, number, char)
    assert isinstance(result, tuple)
    assert len(result) == 3
    pw1, pw2, pw3 = result
    assert len(pw1) == 8
    assert len(pw2) == 12
    assert len(pw3) == 14
