# Password Generator

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![Powered by Supabase](https://img.shields.io/badge/Powered%20by-Supabase-3ECF8E?logo=supabase&logoColor=white)


A simple and secure password generator built with **Streamlit** for the frontend and **Supabase** for backend storage. It helps users create strong and easy to remember passwords based on user inputs.

## Features
 - Generate 3 secure passwords from below user's inputs:
  - Two words
  - A number 
  - A special character
- Inputs validation (no accents, only letters/digits)
- Passwords include digits, symbols, and capital letters
- Copy buttons with toast notifications
- Supabase integration for storing generated passwords
- Session tracking via UUID
- Real-time stats (number of passwords generated)

## How It Works
1. Enter two words (letters only, no accents)
2. Add a number (1–10 digits)
3. Choose a special character
4. Click **Generate** to receive 3 strong passwords

Each password is built from your inputs, respecting the rules below:
- At least 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 special character

## Tech Stack
- **Streamlit** – UI and form handling
- **Supabase** – Database and session tracking
- **Python** – Business logic and validation
- **Regex** – filter and check security inputs
- **Github** – To share this project
- `.env` – Environment variables (Supabase credentials)

## Notes
- If Supabase is unavailable, the app still works — passwords are generated but not stored.
- All inputs are validated both in the interface and backend.
- This project is designed for clarity, modularity, and future scalability.


## Project Structure
PasswordsGenerator/
│
├── venv/                      ← Virtual environment (do not modify)
├── app.py                     ← Main entry point (Streamlit interface)
├── business_logic.py          ← Core logic (input validation, password generation)
├── supabase_client.py         ← Supabase connection setup (URL, API key, error handling)
├── utils.py                   ← Utility functions (session management, database insertion, stats)
│
├── .env                       ← Sensitive environment variables (excluded from version control)
├── .gitignore                 ← Files/folders to ignore (e.g. .env, venv/)
├── requirements.txt           ← Python dependencies
├── schema.sql                 ← Supabase database schema definition
├── test_business_logic.py     ← Unit tests for business logic
├── README.md                  ← Project overview and instructions (for GitHub)

## License
MIT License — feel free to use, modify, and share.

## Author
Made with care by [Wilfried Amany](https://github.com/WilfriedAmany)


