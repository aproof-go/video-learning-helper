import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';
import { dbManager } from '@/lib/supabase-server';

// 获取用户的分析任务列表
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

    // 获取用户的任务列表
    const tasks = await dbManager.getUserTasks(user.id);

    return NextResponse.json(tasks);

  } catch (error) {
    console.error('获取任务列表错误:', error);
    
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

// 创建新的分析任务
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
    const { video_id, video_segmentation, transition_detection, audio_transcription, report_generation } = body;

    // 验证必填字段
    if (!video_id) {
      return NextResponse.json(
        { error: "视频ID是必需的" },
        { status: 400 }
      );
    }

    // 验证视频是否存在且属于当前用户
    const video = await dbManager.getVideoById(video_id);
    if (!video) {
      return NextResponse.json(
        { error: "视频不存在" },
        { status: 404 }
      );
    }

    if (video.user_id !== user.id) {
      return NextResponse.json(
        { error: "无权访问此视频" },
        { status: 403 }
      );
    }

    // 创建分析任务数据
    const taskData = {
      video_id,
      user_id: user.id,
      video_segmentation: video_segmentation || false,
      transition_detection: transition_detection || false,
      audio_transcription: audio_transcription || false,
      report_generation: report_generation || false,
      status: 'pending',
      progress: '{}',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    console.log('📝 Creating analysis task:', {
      video_id,
      user_id: user.id,
      video_segmentation,
      transition_detection,
      audio_transcription,
      report_generation
    });

    // 创建分析任务
    const newTask = await dbManager.createTask(taskData);

    console.log('✅ Analysis task created successfully:', newTask.id);

    return NextResponse.json(newTask, { status: 201 });

  } catch (error) {
    console.error('创建分析任务错误:', error);
    
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
          { error: "分析任务已存在" },
          { status: 409 }
        );
      }
      
      if (error.message.includes('foreign key')) {
        return NextResponse.json(
          { error: "关联的视频不存在" },
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