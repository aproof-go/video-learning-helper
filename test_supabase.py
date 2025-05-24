#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv("config.env")

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tjxqzmrmybrcmkflaimq.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg")

print(f"Connecting to Supabase: {SUPABASE_URL}")

# 创建Supabase客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def test_connection():
    """测试Supabase连接"""
    try:
        # 测试用户表
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Users table exists. Count: {result.count}")
        
        # 测试视频表
        try:
            result = supabase.table("videos").select("count", count="exact").execute()
            print(f"✅ Videos table exists. Count: {result.count}")
        except Exception as e:
            print(f"❌ Videos table error: {e}")
            
        # 测试分析任务表
        try:
            result = supabase.table("analysis_tasks").select("count", count="exact").execute()
            print(f"✅ Analysis tasks table exists. Count: {result.count}")
        except Exception as e:
            print(f"❌ Analysis tasks table error: {e}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_video_insert():
    """测试视频插入"""
    try:
        video_data = {
            "id": "test-video-123",
            "title": "Test Video",
            "filename": "test.mp4",
            "file_size": 1024,
            "format": "mp4",
            "status": "uploaded",
            "user_id": "upload_test@example.com",
            "file_url": "/uploads/test.mp4"
        }
        
        result = supabase.table("videos").insert(video_data).execute()
        print(f"✅ Video insert successful: {result.data}")
        
        # 清理测试数据
        supabase.table("videos").delete().eq("id", "test-video-123").execute()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Video insert error: {e}")

if __name__ == "__main__":
    print("=== Supabase Connection Test ===")
    test_connection()
    print("\n=== Video Insert Test ===")
    test_video_insert() 