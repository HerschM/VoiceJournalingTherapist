import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv(".env.local")

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))

if not url or not key:
    print("Warning: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY) must be set in .env.local")

supabase: Client = create_client(url, key)
