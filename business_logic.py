import secrets
import re
# BUSINESS LOGIC

# Cryptographically secure RNG — single instance used throughout the module
_rng = secrets.SystemRandom()

# Centralized list of allowed special characters
allowed_special_chars = ["@", "!", "_", "#", "$", "%", "&", "*"]


# Step 1: Validate user inputs
#
# Design note — two error-reporting patterns coexist intentionally:
#   • validate_inputs returns (bool, str): used directly by unit tests that need
#     fine-grained assertions on the error message without raising exceptions.
#   • generate_passwords raises ValueError: used by app.py in a try/except block,
#     which is the idiomatic way for an orchestration function to signal failures.
# Both patterns are coherent with their respective call sites; the coexistence is
# deliberate, not accidental.
def validate_inputs(word1, word2, number, special_char):
    """
    Validate the four user inputs before password generation.

    Parameters:
    - word1 (str): First word — must contain only ASCII letters, 2 to 20 chars.
    - word2 (str): Second word — same rules as word1.
    - number (str): Digit string — 1 to 10 digits, no letters or spaces.
    - special_char (str): Must be one of allowed_special_chars.

    Returns:
    - (True, concatenated_inputs): All inputs are valid; concatenated_inputs is
      the lowercased concatenation of all four inputs with no spaces.
    - (False, error_message): Validation failed; error_message references the
      failing field and the rule that was violated.

    Note: this function returns a (bool, str) tuple rather than raising an
    exception so that unit tests can assert on the error message directly.
    See generate_passwords for the ValueError-raising counterpart.
    """
    # Validate word1: only letters a–z or A–Z, length between 2 and 20
    if not re.fullmatch(r"[a-zA-Z]{2,20}", word1):
        return False, "word1 must contain only letters (a–z or A–Z), no accents or symbols, and be 2 to 20 characters long."

    # Validate word2: same rules as word1
    if not re.fullmatch(r"[a-zA-Z]{2,20}", word2):
        return False, "word2 must contain only letters (a–z or A–Z), no accents or symbols, and be 2 to 20 characters long."

    # Validate number: only digits, length between 1 and 10
    if not re.fullmatch(r"\d{1,10}", number):
        return False, "number must contain 1 to 10 digits with no spaces or letters."

    # Validate special_char: must be in the allowed list
    if special_char not in allowed_special_chars:
        return False, "special_char must be one of the allowed characters."

    # Combine all inputs into one string, lowercase, no spaces
    concatenated_inputs = (word1 + word2 + number + special_char).lower().replace(" ", "")

    # Check that the combined string is at least 8 characters long
    if len(concatenated_inputs) < 8:
        return False, "The combined input must be at least 8 characters long."

    # If all checks pass, return True and the cleaned string
    return True, concatenated_inputs


# Step 2 & 3: Extract components and split the combined string
def extract_and_split(word1, word2, concatenated_inputs):
    """
    Extract character fragments from word1, word2, and their concatenation.

    Parameters:
    - word1 (str): First word (pre-normalized to lowercase by generate_passwords).
    - word2 (str): Second word (same remark).
    - concatenated_inputs (str): The lowercased combined string returned by
      validate_inputs (word1 + word2 + number + special_char, lowercased).

    Returns a 6-tuple:
    - first_last_words  (list[str]): First+last letter of each word.
    - two_first_words   (list[str]): First 2 letters of each word.
    - three_first_words (list[str]): First 3 letters of each word.
    - tertil_from_concat  (list[str]): concatenated_inputs split into 3 parts.
    - quartil_from_concat (list[str]): concatenated_inputs split into 4 parts.
    - quintil_from_concat (list[str]): concatenated_inputs split into 5 parts.

    Note: word-level fragments preserve the casing of word1/word2 as passed in.
    generate_passwords lowercases word1/word2 before calling this function so
    that the entire fragment pool is case-uniform.
    """
    # Extract first and last letters of each word
    first_last_words = [word1[0] + word1[-1], word2[0] + word2[-1]]

    # Extract first two letters of each word
    two_first_words = [word1[:2], word2[:2]]

    # Extract first three letters of each word
    three_first_words = [word1[:3], word2[:3]]

    # Split the combined string into 3 parts (tertiles)
    tertil_size = len(concatenated_inputs) // 3
    tertil_from_concat = [
        concatenated_inputs[:tertil_size],
        concatenated_inputs[tertil_size:2*tertil_size],
        concatenated_inputs[2*tertil_size:]
    ]

    # Split the combined string into 4 parts (quartiles)
    quartil_size = len(concatenated_inputs) // 4
    quartil_from_concat = [
        concatenated_inputs[:quartil_size],
        concatenated_inputs[quartil_size:2*quartil_size],
        concatenated_inputs[2*quartil_size:3*quartil_size],
        concatenated_inputs[3*quartil_size:]
    ]

    # Split the combined string into 5 parts (quintiles)
    quintil_size = len(concatenated_inputs) // 5
    quintil_from_concat = [
        concatenated_inputs[:quintil_size],
        concatenated_inputs[quintil_size:2*quintil_size],
        concatenated_inputs[2*quintil_size:3*quintil_size],
        concatenated_inputs[3*quintil_size:4*quintil_size],
        concatenated_inputs[4*quintil_size:]
    ]

    return first_last_words, two_first_words, three_first_words, tertil_from_concat, quartil_from_concat, quintil_from_concat


# Step 4: Merge all fragments and remove duplicates
def build_final_list(word1, word2, number, special_char,
                     first_last_words, two_first_words, three_first_words,
                     tertil_from_concat, quartil_from_concat, quintil_from_concat):
    """
    Merge all character fragments into a single deduplicated pool.

    Parameters:
    - word1, word2 (str): Words (pre-normalized to lowercase by generate_passwords).
    - number (str): Digit string as entered by the user.
    - special_char (str): Special character chosen by the user.
    - first_last_words, two_first_words, three_first_words (list[str]):
      Word-level fragments from extract_and_split.
    - tertil_from_concat, quartil_from_concat, quintil_from_concat (list[str]):
      Concatenation splits from extract_and_split.

    Returns:
    - unique_finale_list (list[str]): Deduplicated list of all fragments,
      used as the random assembly pool in generate_password.
    """
    # Combine all fragments into one list
    final_list = (
        [word1, word2, number, special_char] +
        first_last_words +
        two_first_words +
        three_first_words +
        tertil_from_concat +
        quartil_from_concat +
        quintil_from_concat
    )

    # Remove duplicates by converting to a set, then back to a list
    unique_finale_list = list(set(final_list))
    return unique_finale_list


# Step 5: Generate a password with required rules
def generate_password(start_list, unique_finale_list, target_length, number, special_char):
    """
    Assemble a single password of exactly target_length characters.

    Algorithm:
    1. Start with a random element from start_list (a quartile or tertile).
    2. Append random fragments from unique_finale_list until target_length is reached.
    3. Trim to exactly target_length characters.
    4. Inject the number: effective_number = number[:target_length - 1] ensures
       the number never fills the entire password, always leaving at least one
       slot for the special character. If the full number fits, it is used as-is.
    5. Inject the special_char at position 0 if not already present.
    6. Capitalize 1–2 random letter positions (index-based, not value-based,
       so each position is considered independently).

    Parameters:
    - start_list (list[str]): Pool for the mandatory first fragment.
    - unique_finale_list (list[str]): Full deduplicated fragment pool.
    - target_length (int): Exact desired password length (8, 12, or 14).
    - number (str): Digit string — injected as effective_number.
    - special_char (str): Special character — always present in the result.

    Returns:
    - password (str): Exactly target_length characters, containing at least
      one digit sequence, one special character, and one uppercase letter.
    """
    # Start the password with a required element from the start list
    password = _rng.choice(start_list)

    # Add random fragments until the password reaches the target length
    while len(password) < target_length:
        fragment = _rng.choice(unique_finale_list)
        password += fragment

    # Trim the password to the exact target length
    password = password[:target_length]

    # Clamp the number to target_length - 1 characters to always leave at least one
    # position for the special character. This prevents a length violation when
    # len(number) >= target_length (e.g. an 8-digit number with target_length=8).
    effective_number = number[:target_length - 1]

    # Ensure the effective number is included
    if effective_number not in password:
        password = password[:-len(effective_number)] + effective_number

    # Ensure the special character is included
    if special_char not in password:
        password = special_char + password[1:]

    # Capitalize 1 or 2 random letters using index-based selection to avoid
    # capitalizing all occurrences of the same letter
    letter_indices = [i for i, c in enumerate(password) if c.isalpha()]
    if letter_indices:
        to_cap_indices = set(_rng.sample(letter_indices, min(2, len(letter_indices))))
        password = ''.join(
            c.upper() if i in to_cap_indices else c
            for i, c in enumerate(password)
        )

    return password


# Main function: orchestrates all steps to generate 3 passwords
def generate_passwords(word1, word2, number, special_char):
    """
    Orchestrate the full password generation pipeline and return 3 passwords.

    Inputs are normalized to lowercase before fragment extraction so that the
    entire fragment pool is case-uniform; all uppercase letters in the final
    passwords come exclusively from the controlled capitalization step in
    generate_password (1–2 random positions per password).

    Parameters:
    - word1, word2 (str): Words entered by the user (letters only, any case).
    - number (str): Digit string entered by the user (1–10 digits).
    - special_char (str): Special character selected by the user.

    Returns:
    - (pw1, pw2, pw3): Tuple of 3 passwords with lengths 8, 12, and 14.

    Raises:
    - ValueError: If any input fails validation (message references the
      failing field). Callers should catch this and display the message.

    Note: unlike validate_inputs (which returns a (bool, str) tuple for direct
    test assertions), this function raises ValueError so that app.py can use a
    clean try/except block without isinstance checks on the return value.
    """
    # Step 1: validate inputs — raises ValueError on invalid input
    valid, result = validate_inputs(word1, word2, number, special_char)
    if not valid:
        raise ValueError(result)

    # If valid, use the cleaned combined string
    concatenated_inputs = result

    # Normalize word1 and word2 to lowercase so all word-level fragments
    # (first+last, two-first, three-first) enter the pool in uniform case.
    # Uppercase letters in the final passwords come exclusively from the
    # index-based capitalization step inside generate_password.
    word1 = word1.lower()
    word2 = word2.lower()

    # Step 2 & 3: extract components and split string
    first_last, two_first, three_first, tertil, quartil, quintil = extract_and_split(word1, word2, concatenated_inputs)

    # Step 4: build the final list of fragments
    unique_finale_list = build_final_list(word1, word2, number, special_char,
                                          first_last, two_first, three_first,
                                          tertil, quartil, quintil)

    # Step 5: generate 3 passwords with different lengths and starting rules
    pw1 = generate_password(quartil, unique_finale_list, 8, number, special_char)   # Starts with a quartile
    pw2 = generate_password(tertil, unique_finale_list, 12, number, special_char)   # Starts with a tertile
    pw3 = generate_password(tertil, unique_finale_list, 14, number, special_char)   # Starts with a tertile

    return pw1, pw2, pw3
