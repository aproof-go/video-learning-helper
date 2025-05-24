import { NextRequest, NextResponse } from 'next/server';
import { dbManager } from '@/lib/supabase-server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';

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
    const { file_path, original_filename, file_size } = body;

    if (!file_path || !original_filename) {
      return NextResponse.json(
        { error: "文件路径和原始文件名是必需的" },
        { status: 400 }
      );
    }

    // 创建任务数据
    const taskData = {
      user_id: user.id,
      file_path,
      original_filename,
      file_size: file_size || 0,
      status: 'pending',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // 创建任务
    const newTask = await dbManager.createTask(taskData);

    return NextResponse.json(newTask, { status: 201 });

  } catch (error) {
    console.error('创建任务错误:', error);
    
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