import streamlit as st
import os
from supabase import create_client, Client

# Retrieve Supabase configuration from st.secrets, environment variables, or fallback
SUPABASE_URL = None
SUPABASE_KEY = None

try:
    if hasattr(st, "secrets"):
        if "SUPABASE_URL" in st.secrets:
            SUPABASE_URL = str(st.secrets["SUPABASE_URL"]).strip()
        if "SUPABASE_KEY" in st.secrets:
            SUPABASE_KEY = str(st.secrets["SUPABASE_KEY"]).strip()
except Exception:
    pass

if not SUPABASE_URL:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
if not SUPABASE_KEY:
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Safe fallback for cloud deployments without configured secrets
if not SUPABASE_URL:
    SUPABASE_URL = "https://rmkqfnouofnyxnkgzgkg.supabase.co"
if not SUPABASE_KEY:
    SUPABASE_KEY = "sb_publishable_Kq9HCjaJ02m-jOdaQgyGQA_SfOHbWEd"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Failed to initialize Supabase client: {e}")
    supabase = None