import os
from pathlib import Path
from dotenv import load_dotenv

# Locate .env relative to this file's location (src/config.py -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL",)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY must be set in .env")
