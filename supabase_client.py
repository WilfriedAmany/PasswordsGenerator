from supabase import create_client  # Imports the function to create a Supabase client instance
import os                           # Imports the 'os' module to access environment variables
from dotenv import load_dotenv      # Imports the function to load variables from a .env file

load_dotenv()                       # Loads environment variables from the .env file into the system environment

url = os.getenv("SUPABASE_URL")     # Retrieves the Supabase URL from environment variables
key = os.getenv("SUPABASE_KEY")     # Retrieves the Supabase API key from environment variables

supabase = None                     # Initializes the Supabase client as None by default
supabase_connected = False          # Flag to track connection status

try:
    supabase = create_client(url, key)  # Attempts to create the Supabase client

    # create_client only builds the client object — no network call is made at this point.
    # A lightweight probe request is required to verify that the Supabase service is
    # actually reachable (DNS resolution, authentication, network path). Without this
    # probe, supabase_connected would be True even when all subsequent requests fail,
    # causing the UI to display a misleading "success" message.
    supabase.table("passwords").select("id").limit(1).execute()

    supabase_connected = True           # Sets the flag to True only if the probe succeeds
except Exception as e:
    print("Supabase connection failed:", e)  # Logs the error if connection or probe fails
