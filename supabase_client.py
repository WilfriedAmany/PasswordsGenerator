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
    supabase_connected = True           # Sets the flag to True if successful
except Exception as e:
    print("Supabase connection failed:", e)  # Logs the error if connection fails
