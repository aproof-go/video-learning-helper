import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';

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

    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: "未找到上传文件" },
        { status: 400 }
      );
    }

    // 验证文件类型
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: "不支持的文件类型。请上传MP4、AVI、MOV或MKV格式的视频文件" },
        { status: 400 }
      );
    }

    // 验证文件大小 (100MB限制)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: "文件大小不能超过100MB" },
        { status: 400 }
      );
    }

    // 创建上传目录
    const uploadsDir = path.join(process.cwd(), 'public', 'uploads');
    if (!existsSync(uploadsDir)) {
      await mkdir(uploadsDir, { recursive: true });
    }

    // 生成唯一文件名
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 15);
    const fileExtension = path.extname(file.name);
    const fileName = `${timestamp}_${randomStr}${fileExtension}`;
    const filePath = path.join(uploadsDir, fileName);

    // 保存文件
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    await writeFile(filePath, buffer);

    // 返回文件信息
    const relativePath = `/uploads/${fileName}`;
    
    return NextResponse.json({
      message: "文件上传成功",
      file_path: relativePath,
      original_filename: file.name,
      file_size: file.size,
      upload_time: new Date().toISOString()
    });

  } catch (error) {
    console.error('文件上传错误:', error);
    
    if (error instanceof APIError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode }
      );
    }

    return NextResponse.json(
      { error: "文件上传失败" },
      { status: 500 }
    );
  }
} 