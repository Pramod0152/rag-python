from supabase import create_client, Client
import os
from config import SUPABASE_KEY, SUPABASE_URL

_supabase: Client = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase
