import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def keep_alive():
    response = supabase.table("list_items").select("id").limit(1).execute()
    print("Supabase keep-alive ping successful.")

if __name__ == "__main__":
    keep_alive()
