import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';
import { dbManager } from '@/lib/supabase-server';

// 获取用户的视频列表
export async function GET(request: NextRequest) {
  try {
    // 验证JWT令牌
    const userPayload = getCurrentUserFromRequest(request);
    if (!userPayload) {
      return NextResponse.json(
        { error: "未授权访问" },
        { status: 401 }
      );
    }

    // 获取用户信息
    const user = await dbManager.getUserByEmail(userPayload.sub);
    if (!user) {
      return NextResponse.json(
        { error: "用户不存在" },
        { status: 404 }
      );
    }

    // 获取查询参数
    const { searchParams } = new URL(request.url);
    const skip = parseInt(searchParams.get('skip') || '0');
    const limit = parseInt(searchParams.get('limit') || '100');
    const includeTasks = searchParams.get('include_tasks') === 'true';

    // 获取用户的视频列表
    const videos = await dbManager.getUserVideos(user.id, skip, limit);

    // 如果需要包含任务信息
    if (includeTasks) {
      for (const video of videos) {
        video.tasks = await dbManager.getVideoAnalysisTasks(video.id);
      }
    }

    return NextResponse.json(videos);

  } catch (error) {
    console.error('获取视频列表错误:', error);
    
    if (error instanceof APIError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode }
      );
    }

    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
}

// 创建新的视频记录
export async function POST(request: NextRequest) {
  try {
    // 验证JWT令牌
    const userPayload = getCurrentUserFromRequest(request);
    if (!userPayload) {
      return NextResponse.json(
        { error: "未授权访问" },
        { status: 401 }
      );
    }

    // 获取用户信息
    const user = await dbManager.getUserByEmail(userPayload.sub);
    if (!user) {
      return NextResponse.json(
        { error: "用户不存在" },
        { status: 404 }
      );
    }

    const body = await request.json();
    const { title, filename, file_size, file_url, description } = body;

    // 验证必填字段
    if (!title || !filename || !file_size || !file_url) {
      return NextResponse.json(
        { error: "标题、文件名、文件大小和文件URL是必需的" },
        { status: 400 }
      );
    }

    // 创建视频数据
    const videoData = {
      user_id: user.id,
      title: title.trim(),
      filename: filename.trim(),
      file_size: parseInt(file_size),
      file_url: file_url.trim(),
      description: description?.trim() || '',
      status: 'uploaded',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    console.log('📝 Creating video record:', {
      user_id: user.id,
      title: videoData.title,
      filename: videoData.filename,
      file_size: videoData.file_size,
      file_url_preview: videoData.file_url.substring(0, 100) + '...'
    });

    // 创建视频记录
    const newVideo = await dbManager.createVideo(videoData);

    console.log('✅ Video record created successfully:', newVideo.id);

    return NextResponse.json(newVideo, { status: 201 });

  } catch (error) {
    console.error('创建视频记录错误:', error);
    
    if (error instanceof APIError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode }
      );
    }

    // 处理数据库约束错误
    if (error instanceof Error) {
      if (error.message.includes('duplicate key')) {
        return NextResponse.json(
          { error: "视频记录已存在" },
          { status: 409 }
        );
      }
      
      if (error.message.includes('foreign key')) {
        return NextResponse.json(
          { error: "关联数据不存在" },
          { status: 400 }
        );
      }
    }

    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 