import { NextRequest, NextResponse } from 'next/server';
import { dbManager } from '@/lib/supabase-server';
import { createAccessToken, hashPassword, APIError } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, name } = body;

    if (!email || !password || !name) {
      return NextResponse.json(
        { error: "邮箱、密码和姓名是必需的" },
        { status: 400 }
      );
    }

    // 检查邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "邮箱格式不正确" },
        { status: 400 }
      );
    }

    // 检查密码长度
    if (password.length < 6) {
      return NextResponse.json(
        { error: "密码长度至少为6位" },
        { status: 400 }
      );
    }

    // 检查用户是否已存在
    const existingUser = await dbManager.getUserByEmail(email);
    if (existingUser) {
      return NextResponse.json(
        { error: "该邮箱已被注册" },
        { status: 400 }
      );
    }

    // 加密密码
    const passwordHash = await hashPassword(password);

    // 创建用户
    const newUser = await dbManager.createUser({
      email,
      name,
      password_hash: passwordHash,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });

    // 创建JWT令牌
    const accessToken = createAccessToken(newUser.email);

    return NextResponse.json({
      access_token: accessToken,
      token_type: "bearer",
      user: {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name,
        created_at: newUser.created_at
      }
    }, { status: 201 });

  } catch (error) {
    console.error('注册错误:', error);
    
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