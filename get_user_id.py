#!/usr/bin/env python3

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('config.env')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://tjxqzmrmybrcmkflaimq.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg')

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
result = supabase.table('users').select('id, email').eq('email', 'upload_test@example.com').execute()
print('User data:', result.data) 