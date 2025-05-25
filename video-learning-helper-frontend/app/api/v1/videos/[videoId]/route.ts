import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';
import { dbManager } from '@/lib/supabase-server';

// 获取特定视频详情
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

    // 获取视频详情
    const video = await dbManager.getVideoById(videoId);
    if (!video) {
      return NextResponse.json(
        { error: "视频不存在" },
        { status: 404 }
      );
    }

    // 验证用户权限
    if (video.user_id !== user.id) {
      return NextResponse.json(
        { error: "无权访问此视频" },
        { status: 403 }
      );
    }

    return NextResponse.json(video);

  } catch (error) {
    console.error('获取视频详情错误:', error);
    
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

// 删除特定视频
export async function DELETE(
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

    // 获取视频详情以验证权限
    const video = await dbManager.getVideoById(videoId);
    if (!video) {
      return NextResponse.json(
        { error: "视频不存在" },
        { status: 404 }
      );
    }

    // 验证用户权限
    if (video.user_id !== user.id) {
      return NextResponse.json(
        { error: "无权删除此视频" },
        { status: 403 }
      );
    }

    // 删除视频（软删除）
    await dbManager.deleteVideo(videoId);

    return NextResponse.json({ 
      message: "视频删除成功" 
    });

  } catch (error) {
    console.error('删除视频错误:', error);
    
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