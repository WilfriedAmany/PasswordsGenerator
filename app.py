# Import required libraries
import streamlit as st
from business_logic import generate_passwords, allowed_special_chars  # Import the main password generation function
from utils import save_password_to_supabase, ensure_session_exists, get_password_count, mark_password_as_copied  # Supabase helper functions
from supabase_client import supabase_connected
import re

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
    special_char = st.selectbox("Choose a special character", allowed_special_chars)

    # Submit button to trigger password generation
    submitted = st.form_submit_button("Generate")

# Process the form submission
if submitted:
    # Step 1: Check for empty fields
    if not word1 or not word2 or not number:
        st.warning("Please fill in all fields before generating.")

    # Step 2: Validate word1 (only letters, no accents or symbols)
    elif not re.fullmatch(r"[a-zA-Z]{2,20}", word1):
        st.warning("Word1 must contain only letters (a–z or A–Z), no accents or symbols, and be 2 to 20 characters long.")

    # Step 3: Validate word2 (same rules as word1)
    elif not re.fullmatch(r"[a-zA-Z]{2,20}", word2):
        st.warning("Word2 must contain only letters (a–z or A–Z), no accents or symbols, and be 2 to 20 characters long.")

    # Step 4: Validate number (only digits, length between 1 and 10)
    elif not re.fullmatch(r"\d{1,10}", number):
        st.warning("Number must contain 1 to 10 digits, no spaces or letters.")

    # Step 5: Validate special_char (must be in the allowed list)
    elif special_char not in allowed_special_chars:
        st.warning("Please select a valid special character.")

    else:
        # Step 6: Call the password generation function from business_logic.py
        result = generate_passwords(word1, word2, number, special_char)

        # Step 7: If the result is a string, it means validation failed and an error message was returned
        if isinstance(result, str):
            st.error(result)  # Display the error message to the user
        else:
            # Step 8: If result is a list of passwords, display them
            st.success("Here are your generated passwords:")

            # Step 9: Store the latest passwords in session state (limit to 3)
            st.session_state.passwords = result[:3]

            # Step 10: Save each password to Supabase with the original input components
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




