# Password Generator

A web-based password generator built with **Streamlit** (UI) and **Supabase** (database).

The user enters two words, a number, and a special character. Three passwords are generated at lengths 8, 12, and 14 characters.

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/Scripts/activate   # Windows (bash)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Supabase credentials
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY

# 4. Run the app
streamlit run app.py
```

---

## How It Works

### Input rules

| Field | Constraint |
|---|---|
| `word1` | Letters only (a–z, A–Z), 2–20 characters |
| `word2` | Same as word1 |
| `number` | Digits only, 1–10 characters |
| `special_char` | One of: `@ ! _ # $ % & *` |
| Combined | All four inputs concatenated must be ≥ 8 characters |

### Password generation pipeline

```
validate_inputs          — validates format rules, returns lowercased concat
  ↓
normalize (word1/word2 → lowercase)
  ↓
extract_and_split        — builds word fragments + tertile/quartile/quintile splits
  ↓
build_final_list         — merges and deduplicates all fragments into one pool
  ↓
generate_password ×3     — assembles passwords of lengths 8, 12, 14
```

---

## Design Notes

### Input normalization

`word1` and `word2` are converted to **lowercase** before any fragment extraction.
This means the entire fragment pool (`unique_finale_list`) is case-uniform.
Fragments like `"alpha"`, `"al"`, `"alp"`, `"aa"` are used — never `"Alpha"`, `"Al"`, etc.

### Controlled capitalization

All uppercase letters in generated passwords come exclusively from the
**index-based capitalization step** inside `generate_password`:
1–2 random character positions are selected and uppercased.
This gives predictable, bounded uppercase behavior regardless of input casing.

### Number truncation (`effective_number`)

When `len(number) >= target_length`, injecting the full number would overflow
the password or leave no room for the special character. The fix:

```python
effective_number = number[:target_length - 1]
```

This clamps the number to at most `target_length - 1` characters, always leaving
one position for the special character. The final password length is always exactly
`target_length`.

Example: `number="12345678"`, `target_length=8` → `effective_number="1234567"` (7 chars),
leaving 1 slot for the special character.

### Error reporting — two patterns

| Function | Pattern | Reason |
|---|---|---|
| `validate_inputs` | Returns `(bool, str)` | Used by unit tests for direct assertions on the error message |
| `generate_passwords` | Raises `ValueError` | Used by `app.py` in a `try/except` block — idiomatic for orchestration |

Both patterns are coherent with their call sites. The coexistence is deliberate.

---

## Project Structure

```
app.py                  — Streamlit UI, form, session state, callbacks
business_logic.py       — Validation, fragment extraction, password assembly
utils.py                — Supabase operations (no Streamlit dependency)
supabase_client.py      — Supabase client init, supabase_connected flag
test_business_logic.py  — 44 pytest unit tests (100% passing)
requirements.txt        — 4 pinned direct dependencies
```

---

## Running Tests

```bash
pytest test_business_logic.py
```

### Test coverage

| Group | Tests |
|---|---|
| `validate_inputs` | 15 |
| `extract_and_split` | 4 |
| `build_final_list` | 3 |
| `generate_password` — normal cases | 6 |
| `generate_password` — long number / clamped prefix | 4 |
| `generate_passwords` — full flow | 9 |
| Parametrized | 3 |
| **Total** | **44** |

Key behaviors covered:
- All allowed special characters validated individually
- Passwords always contain the (clamped) number and the special character
- Passwords are always exactly the requested length (8, 12, 14)
- `effective_number` prefix is present when number is truncated
- Invalid inputs raise `ValueError` referencing the failing field
- Generated passwords always contain at least one uppercase letter

---

## Stack

- Python 3.12.3
- Streamlit 1.50.0
- Supabase 2.20.0
- python-dotenv 1.1.1
- pytest 9.0.2

---

© Wilfried AMANY
