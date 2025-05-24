#!/usr/bin/env python3

import uuid
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('config.env')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://tjxqzmrmybrcmkflaimq.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg')

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# First get the correct user UUID
user_result = supabase.table('users').select('id, email').eq('email', 'upload_test@example.com').execute()
if not user_result.data:
    print("❌ User not found")
    exit(1)

user_uuid = user_result.data[0]['id']
print(f"✅ Found user UUID: {user_uuid}")

# Now test video insertion with correct UUID
video_data = {
    'id': str(uuid.uuid4()),
    'title': 'Test Video with Correct UUID',
    'filename': 'test_correct.mp4',
    'file_size': 1024,
    'format': 'mp4',
    'status': 'uploaded',
    'user_id': user_uuid,  # Use correct UUID
    'file_url': '/uploads/test_correct.mp4'
}

print(f'Testing video insert with correct user UUID: {user_uuid}')
try:
    result = supabase.table('videos').insert(video_data).execute()
    print('✅ Video insert successful:', result.data[0]['id'])
    
    # Verify the video was inserted
    verify_result = supabase.table('videos').select('*').eq('id', video_data['id']).execute()
    print('✅ Video verified in database:', len(verify_result.data) > 0)
    
    # Clean up
    supabase.table('videos').delete().eq('id', video_data['id']).execute()
    print('✅ Cleaned up test data')
except Exception as e:
    print('❌ Error:', e) 