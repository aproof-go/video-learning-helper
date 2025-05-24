import { NextRequest, NextResponse } from 'next/server';
import { dbManager } from '@/lib/supabase-server';
import { createAccessToken, verifyPassword, APIError } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json(
        { error: "邮箱和密码是必需的" },
        { status: 400 }
      );
    }

    // 查找用户
    const user = await dbManager.getUserByEmail(email);
    if (!user) {
      return NextResponse.json(
        { error: "用户不存在或密码错误" },
        { status: 401 }
      );
    }

    // 验证密码
    const isValidPassword = await verifyPassword(password, user.password_hash);
    if (!isValidPassword) {
      return NextResponse.json(
        { error: "用户不存在或密码错误" },
        { status: 401 }
      );
    }

    // 创建JWT令牌
    const accessToken = createAccessToken(user.email);

    return NextResponse.json({
      access_token: accessToken,
      token_type: "bearer",
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        created_at: user.created_at
      }
    });

  } catch (error) {
    console.error('登录错误:', error);
    
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