from supabase import create_client, Client
from app.core.config import settings

# Initialize the Supabase client using your URL and API key
def get_supabase_client() -> Client:
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    supabase: Client = create_client(url, key)
    return supabase
