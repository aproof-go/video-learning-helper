import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';
import { dbManager } from '@/lib/supabase-server';

// 获取特定分析任务详情
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ taskId: string }> }
) {
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

    const resolvedParams = await params;
    const { taskId } = resolvedParams;

    // 获取分析任务详情
    const task = await dbManager.getTaskById(taskId);
    if (!task) {
      return NextResponse.json(
        { error: "分析任务不存在" },
        { status: 404 }
      );
    }

    // 验证用户权限
    if (task.user_id !== user.id) {
      return NextResponse.json(
        { error: "无权访问此分析任务" },
        { status: 403 }
      );
    }

    return NextResponse.json(task);

  } catch (error) {
    console.error('获取分析任务详情错误:', error);
    
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