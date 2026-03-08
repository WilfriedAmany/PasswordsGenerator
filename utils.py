# utils.py
from supabase_client import supabase, supabase_connected
from datetime import datetime, timezone


def save_password_to_supabase(password, word1, word2, number, special_char, session_id):
    """
    Save a generated password to the Supabase database.
    Parameters:
    - password (str): The generated password
    - word1 (str): First word entered by the user
    - word2 (str): Second word entered by the user
    - number (str): Numeric part entered by the user
    - special_char (str): Special character selected by the user
    - session_id (str): UUID identifying the current user session
    """
    if not supabase_connected:
        return  # Skip saving if Supabase is not connected

    try:
        supabase.table("passwords").insert({
            "user_id": session_id,
            "value": password,
            "copied": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "word1": word1,
            "word2": word2,
            "numeric": int(number),
            "special_char": special_char
        }).execute()
    except Exception as e:
        print("Failed to save password to Supabase:", e)


def ensure_session_exists(session_id):
    """
    Record the session ID in the Supabase 'users' table if not already present.
    Does nothing if Supabase is not connected.
    Parameters:
    - session_id (str): UUID identifying the current user session
    """
    if not supabase_connected:
        return

    try:
        existing = supabase.table("users").select("id").eq("id", session_id).execute()
        if not existing.data:
            supabase.table("users").insert({
                "id": session_id,
                "session_start": datetime.now(timezone.utc).isoformat()
            }).execute()
    except Exception as e:
        print("Failed to ensure session in Supabase:", e)


def mark_password_as_copied(password_value, session_id):
    """
    Update the 'copied' status of a password in Supabase when the user clicks 'Copy'.
    Filters by both session_id and value to avoid updating records from other sessions.
    Parameters:
    - password_value (str): The password that was copied
    - session_id (str): UUID identifying the current user session
    """
    if not supabase_connected:
        return

    try:
        query = supabase.table("passwords").update({"copied": True}).eq("value", password_value)
        if session_id:
            query = query.eq("user_id", session_id)
        query.execute()
    except Exception as e:
        print("Failed to mark password as copied in Supabase:", e)


def get_password_count():
    """Return the total number of passwords stored in Supabase, or 0 if unavailable."""
    if not supabase_connected:
        return 0
    try:
        response = supabase.table("passwords").select("id", count="exact").execute()
        return response.count
    except Exception as e:
        print("Failed to retrieve password count from Supabase:", e)
        return 0
