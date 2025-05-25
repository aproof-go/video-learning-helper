import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';
import { dbManager } from '@/lib/supabase-server';

// 获取特定视频的分析任务列表
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ videoId: string }> }
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
    const { videoId } = resolvedParams;

    // 验证视频是否存在且属于当前用户
    const video = await dbManager.getVideoById(videoId);
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

    // 获取视频的分析任务
    const tasks = await dbManager.getVideoAnalysisTasks(videoId);

    return NextResponse.json(tasks);

  } catch (error) {
    console.error('获取视频分析任务错误:', error);
    
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