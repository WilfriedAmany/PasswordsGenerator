import random
import re
# BUSINESS LOGIC

# Centralized list of allowed special characters
allowed_special_chars = ["@", "!", "_", "#", "$", "%", "&", "*"]

# 🔹 Step 1: Validate user inputs
def validate_inputs(word1, word2, number, special_char):
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


# 🔹 Step 2 & 3: Extract components and split the combined string
def extract_and_split(word1, word2, concatenated_inputs):
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
    
    # Return all extracted lists
    return first_last_words, two_first_words, three_first_words, tertil_from_concat, quartil_from_concat, quintil_from_concat


# 🔹 Step 4: Merge all fragments and remove duplicates
def build_final_list(word1, word2, number, special_char,
                     first_last_words, two_first_words, three_first_words,
                     tertil_from_concat, quartil_from_concat, quintil_from_concat):
    
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
    
    # Return the cleaned and unique list
    return unique_finale_list


# 🔹 Step 5: Generate a password with required rules
def generate_password(start_list, unique_finale_list, target_length, number, special_char):
    # Start the password with a required element from the start list
    password = random.choice(start_list)
    
    # Add random fragments until the password reaches the target length
    while len(password) < target_length:
        fragment = random.choice(unique_finale_list)
        password += fragment
    
    # Trim the password to the exact target length
    password = password[:target_length]
    
    # Ensure the number is included
    if number not in password:
        password = password[:-len(number)] + number
    
    # Ensure the special character is included
    if special_char not in password:
        password = special_char + password[1:]
    
    # Capitalize 1 or 2 random letters in the password
    letters = [c for c in password if c.isalpha()]
    if letters:
        to_cap = random.sample(letters, min(2, len(letters)))
        password = ''.join([c.upper() if c in to_cap else c for c in password])
    
    # Return the final password
    return password


# 🔹 Main function: orchestrates all steps to generate 3 passwords
def generate_passwords(word1, word2, number, special_char):
    # Step 1: validate inputs
    valid, result = validate_inputs(word1, word2, number, special_char)
    if not valid:
        return result  # Return error message if inputs are invalid

    # If valid, use the cleaned combined string
    concatenated_inputs = result

    # Step 2 & 3: extract components and split string
    first_last, two_first, three_first, tertil, quartil, quintil = extract_and_split(word1, word2, concatenated_inputs)

    # Step 4: build the final list of fragments
    unique_finale_list = build_final_list(word1, word2, number, special_char,
                                          first_last, two_first, three_first,
                                          tertil, quartil, quintil)

    # Step 5: generate 3 passwords with different lengths and starting rules
    pw1 = generate_password(quartil, unique_finale_list, 8, number, special_char)   # Starts with a quartile
    pw2 = generate_password(tertil, unique_finale_list, 12, number, special_char)  # Starts with a tertile
    pw3 = generate_password(tertil, unique_finale_list, 14, number, special_char)  # Starts with a tertile

    # Return the 3 generated passwords
    return pw1, pw2, pw3

