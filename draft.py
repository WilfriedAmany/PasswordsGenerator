# app.py code
# Import required libraries
import streamlit as st
from business_logic import generate_passwords, allowed_special_chars  # Import the main password generation function
from utils import save_password_to_supabase, ensure_session_exists, get_password_count, mark_password_as_copied  # Supabase helper functions
from supabase_client import supabase_connected

########################################################
# Check Supabase connexion
if supabase_connected:
    st.success("Connection to Supabase: success")
else:
    st.error("Connection to Supabase: failed")

########################################################
# Initialize session state to store generated passwords
if "passwords" not in st.session_state:
    st.session_state.passwords = []

########################################################
# Display the app title
st.title("Password Generator")

# 🎯 Introduction to the Password Generator solution
st.markdown("""
### 🔐 Welcome to Password Generator
This tool helps you create **strong, secure, and memorable passwords** — built from words and numbers that **you choose**.
""")

########################################################
# ✨ Sidebar with tips, branding, and author
with st.sidebar:
    st.markdown("## 💡 Tip")
    st.info("Use words that are easy for you to remember but hard for others to guess.")

    st.markdown("---")
    st.markdown("🔗 [GitHub Repository](https://github.com/.../password-generator)")
    st.markdown("📺 [YouTube Demo](https://youtube.com/...)")
    st.markdown("💼 [LinkedIn Profile](https://www.linkedin.com/in/...)")

    st.markdown("---")
    count = get_password_count()
    st.markdown(f"**Generated passwords :** :green[{count}]")
    st.markdown("Powered by **Streamlit + Supabase**")
    st.markdown("<small style='color:gray;'>© Wilfried AMANY <small>", unsafe_allow_html=True)


########################################################
# 🔧 Display "How it works" and "Benefits" side by side using columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔧 How it works")
    st.markdown("""
    1. Enter two words that are meaningful to you  
    2. Add a number (e.g. birth year, lucky number)  
    3. Choose a special character  
    4. Click **Generate** to get 3 secure passwords  
    """)

with col2:
    st.markdown("### ✅ Key Benefits")
    st.markdown("""
    - 🔒 Strong and complex  
    - 🧠 Easy to remember  
    - 🔢 Includes digits, symbols, and capital letters  
    """)


########################################################
# Ensure a session ID exists and is stored in Supabase
ensure_session_exists()

# Create a form to collect user input
with st.form("password_form"):
    # Input field for the first word (letters only, hidden for privacy)
    word1 = st.text_input("Word1 (letters only)", max_chars=20, type="password")
    
    # Input field for the second word (letters only, hidden for privacy)
    word2 = st.text_input("Word2 (letters only)", max_chars=20, type="password")
    
    # Input field for the number (digits only)
    number = st.text_input("Number (digits only)", max_chars=10)
    
    # Dropdown to select a special character
    special_char = st.selectbox("Choose a special character", ["@", "!", "_", "#", "$", "%", "&", "*"])
    
    # Submit button to trigger password generation
    submitted = st.form_submit_button("Generate")

# Process the form submission
if submitted:
    # Validation from interface to avoid empty fields
    if not word1 or not word2 or not number:
        st.warning("Please fill in all fields before generating.")
    else:
        # Call the password generation function from business_logic.py
        # This function includes all input validation internally
        result = generate_passwords(word1, word2, number, special_char)

        # If the result is a string, it means validation failed and an error message was returned
        if isinstance(result, str):
            st.error(result)  # Display the error message to the user
        else:
            # If result is a list of passwords, display them
            st.success("Here are your generated passwords:")

            # Store the latest passwords in session state (limit to 3)
            st.session_state.passwords = result[:3]

            # Save each password to Supabase with the original input components
            for pwd in st.session_state.passwords:
                save_password_to_supabase(pwd, word1, word2, number, special_char)


# Define the copy handler function
def handle_copy(pwd):
    st.toast(f"Copied: {pwd}")  # Display a toast notification confirming the copy
    mark_password_as_copied(pwd)  # Update the 'copied' status in Supabase
# Display the last generated passwords outside the form
if st.session_state.passwords:
    st.subheader("Last 3 Generated Passwords")
    for i, pwd in enumerate(st.session_state.passwords, 1):
        st.code(pwd)  # Display the password in a code block with native copy icon
        st.button(f"Copy: {pwd}", on_click=lambda p=pwd: handle_copy(p))  # Trigger toast + Supabase update







# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# supabase_client.py
from supabase import create_client  # Imports the function to create a Supabase client instance
import os                           # Imports the 'os' module to access environment variables
from dotenv import load_dotenv      # Imports the function to load variables from a .env file

load_dotenv()                       # Loads environment variables from the .env file into the system environment

url = os.getenv("SUPABASE_URL")     # Retrieves the Supabase URL from environment variables
key = os.getenv("SUPABASE_KEY")     # Retrieves the Supabase API key from environment variables

supabase = create_client(url, key)  # Initializes the Supabase client using the retrieved URL and key



# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# utils.py
from supabase_client import supabase  # Import the Supabase client
from datetime import datetime
import streamlit as st
import uuid

def save_password_to_supabase(password, word1, word2, number, special_char):
    """
    Save a generated password to the Supabase database.

    Parameters:
    - password (str): The generated password
    - word1 (str): First word entered by the user
    - word2 (str): Second word entered by the user
    - number (str): Numeric part entered by the user
    - special_char (str): Special character selected by the user
    """

    # Generate a session ID if not already present in session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Insert the password record into the Supabase 'passwords' table
    supabase.table("passwords").insert({
        "user_id": st.session_state.session_id,
        "value": password,
        "copied": False,
        "timestamp": datetime.utcnow().isoformat(),
        "word1": word1,
        "word2": word2,
        "numeric": int(number),
        "special_char": special_char
    }).execute()



def ensure_session_exists():
    """
    Ensure that a session ID exists in session state and is recorded in the 'users' table.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Check if session already exists in Supabase
    existing = supabase.table("users").select("id").eq("id", st.session_state.session_id).execute()

    if not existing.data:
        # Insert new session into 'users' table
        supabase.table("users").insert({
            "id": st.session_state.session_id,
            "session_start": datetime.utcnow().isoformat()
        }).execute()

# Explication de la fonction ci-dessus:
'''
Tu essaies d’insérer une ligne dans la table passwords avec un champ user_id égal à 20525bad-6be3-43fa-97d4-7d93753ab147,
mais aucune ligne avec cet id n’existe dans la table users.

Pourquoi ça arrive:
Tu as bien généré un session_id dans st.session_state, mais tu n’as pas inséré cette session dans la table users avant d’insérer les mots de passe.
Or, Supabase applique la contrainte suivante :
Chaque user_id dans passwords doit exister dans users.id.

'''

def get_password_count():
    response = supabase.table("passwords").select("id", count="exact").execute()
    return response.count

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# business_logic.py
import random
# BUSINESS LOGIC
# 🔹 Step 1: Validate user inputs
def validate_inputs(word1, word2, number, special_char):
    # Check that word1 contains only letters and is between 2 and 20 characters
    if not (word1.isalpha() and 2 <= len(word1) <= 20):
        return False, "word1 must contain only letters (no accents or special characters) and be 2 to 20 characters long."
    
    # Check that word2 follows the same rules
    if not (word2.isalpha() and 2 <= len(word2) <= 20):
        return False, "word2 must contain only letters (no accents or special characters) and be 2 to 20 characters long."
    
    # Check that number contains only digits, no spaces, and is up to 10 digits long
    if not (number.isdigit() and 1 <= len(number) <= 10):
        return False, "number must contain 1 to 10 digits with no spaces."
    
    # Check that special_char is a valid special character
    if not (special_char in "!@#$%^&*()-_=+[]{};:,.<>?/\\|"):
        return False, "special_char must be a valid special character."
    
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

