# utils.py
from supabase_client import supabase, supabase_connected  # Import the Supabase client
from datetime import datetime
import streamlit as st
import uuid

def save_password_to_supabase(password, word1, word2, number, special_char):
    if not supabase_connected:
        return  # Skip saving if Supabase is not connected
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

'''
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
'''
def ensure_session_exists():
    """
    Vérifie qu'un identifiant de session existe dans Streamlit et l'enregistre dans Supabase si possible.
    """

    # Check if a session ID already exists in Streamlit's session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Generate a new UUID for the session

    # If Supabase is not connected, skip database operations
    if not supabase_connected:
        return  # Avoid errors if Supabase is unavailable

    try:
        # Query Supabase to check if the session ID already exists in the 'users' table
        existing = supabase.table("users").select("id").eq("id", st.session_state.session_id).execute()

        # If no matching session is found, insert a new record into the 'users' table
        if not existing.data:
            supabase.table("users").insert({
                "id": st.session_state.session_id,  # Use the generated session ID
                "session_start": datetime.utcnow().isoformat()  # Record the session start time
            }).execute()
    except Exception as e:
        print("Failed to ensure session in Supabase:", e)  # Log the error for debugging


# Explication de la fonction ci-dessus:
'''
Tu essaies d’insérer une ligne dans la table passwords avec un champ user_id égal à 20525bad-6be3-43fa-97d4-7d93753ab147,
mais aucune ligne avec cet id n’existe dans la table users.

Pourquoi ça arrive:
Tu as bien généré un session_id dans st.session_state, mais tu n’as pas inséré cette session dans la table users avant d’insérer les mots de passe.
Or, Supabase applique la contrainte suivante :
Chaque user_id dans passwords doit exister dans users.id.
'''

def mark_password_as_copied(password_value):
    """
    Update the 'copied' status of a password in Supabase when the user clicks 'Copy'.
    """
    if not supabase_connected:
        return  # Skip if Supabase is not connected
    # Update the first matching password with the given value
    supabase.table("passwords").update({"copied": True}).eq("value", password_value).execute()


def get_password_count():
    response = supabase.table("passwords").select("id", count="exact").execute()
    return response.count

