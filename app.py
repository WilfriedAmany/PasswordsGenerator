# Import required libraries
import streamlit as st
import uuid
from business_logic import generate_passwords, allowed_special_chars
from utils import save_password_to_supabase, ensure_session_exists, get_password_count, mark_password_as_copied
from supabase_client import supabase_connected

########################################################
# Supabase connection status — displayed on every render.
#
# The application is intentionally designed to work without Supabase:
# password generation is entirely local and never depends on the database.
# Supabase is used only for persistence (saving passwords, tracking sessions).
# If the connection is unavailable (network down, misconfigured .env, etc.),
# a warning is shown but no functionality is lost — the app degrades gracefully.
if supabase_connected:
    st.success("Connection to Supabase: success")
else:
    st.warning("⚠️ Connexion à Supabase indisponible. L'application reste utilisable.")

########################################################
# Initialize session state
if "passwords" not in st.session_state:
    st.session_state.passwords = []

# Initialize session ID — managed here and passed explicitly to utils functions
# (utils.py is decoupled from Streamlit and receives session_id as a parameter)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

########################################################
# Display the app title
st.title("Password Generator")

# Introduction
st.markdown("""
### 🔐 Welcome to Password Generator
This tool helps you create **strong, secure, and memorable passwords** — built from words and numbers that **you choose**.
""")

########################################################
# Sidebar with tips, branding, and author
with st.sidebar:
    st.markdown("## 💡 Tip")
    st.info("Use words that are easy for you to remember but hard for others to guess.")

    st.markdown("---")
    st.markdown("🔗 [GitHub Repository](https://github.com/WilfriedAmany/PasswordsGenerator)")
    st.markdown("💼 [LinkedIn Profile](https://www.linkedin.com/in/wa198807)")

    st.markdown("---")
    count = get_password_count()
    st.markdown(f"**Generated passwords :** :green[{count}]")
    st.markdown("Powered by **Streamlit + Supabase**")
    st.caption("© Wilfried AMANY")

########################################################
# Display "How it works" and "Benefits" side by side using columns
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
ensure_session_exists(st.session_state.session_id)

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
    # Check for empty fields — only this UI-level guard is needed here;
    # all format validation is handled by generate_passwords (raises ValueError)
    if not word1 or not word2 or not number:
        st.warning("Please fill in all fields before generating.")
    else:
        try:
            # Generate passwords — raises ValueError if inputs are invalid
            pw1, pw2, pw3 = generate_passwords(word1, word2, number, special_char)

            st.success("Here are your generated passwords:")

            # Store the latest passwords in session state
            st.session_state.passwords = [pw1, pw2, pw3]

            # Save each password to Supabase with the original input components
            for pwd in st.session_state.passwords:
                save_password_to_supabase(pwd, word1, word2, number, special_char, st.session_state.session_id)

        except ValueError as e:
            st.error(str(e))


# Copy handler — defined before the display section that references it
def handle_copy(pwd):
    st.toast(f"Copied: {pwd}")  # Display a toast notification confirming the copy
    mark_password_as_copied(pwd, st.session_state.session_id)  # Update copied status in Supabase


# Display the last generated passwords
if st.session_state.passwords:
    st.subheader("Last 3 Generated Passwords")
    for i, pwd in enumerate(st.session_state.passwords, 1):
        st.code(pwd)  # Display the password in a code block with native copy icon
        st.button(f"Copy: {pwd}", on_click=lambda p=pwd: handle_copy(p))
