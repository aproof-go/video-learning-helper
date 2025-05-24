#!/usr/bin/env python3

import uuid
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('config.env')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://tjxqzmrmybrcmkflaimq.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg')

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

video_data = {
    'id': str(uuid.uuid4()),
    'title': 'Test Video',
    'filename': 'test.mp4',
    'file_size': 1024,
    'format': 'mp4',
    'status': 'uploaded',
    'user_id': 'upload_test@example.com',
    'file_url': '/uploads/test.mp4'
}

print('Testing video insert with UUID:', video_data['id'])
try:
    result = supabase.table('videos').insert(video_data).execute()
    print('✅ Success:', result.data)
    
    # Clean up
    supabase.table('videos').delete().eq('id', video_data['id']).execute()
    print('✅ Cleaned up test data')
except Exception as e:
    print('❌ Error:', e) 