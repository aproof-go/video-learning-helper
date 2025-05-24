import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUserFromRequest, APIError } from '@/lib/auth';
import { supabaseServer } from '@/lib/supabase-server';

// 环境检测函数
const getEnvironment = (): 'development' | 'production' => {
  if (process.env.VERCEL_ENV === 'production') return 'production';
  if (process.env.NODE_ENV === 'production') return 'production';
  return 'development';
};

// 获取存储桶名称
const getStorageBucket = () => {
  const environment = getEnvironment();
  
  switch (environment) {
    case 'production':
      return process.env.SUPABASE_STORAGE_BUCKET_PROD || 'video-learning-prod';
    case 'development':
      return process.env.SUPABASE_STORAGE_BUCKET_DEV || 'video-learning-test';
    default:
      return 'video-learning-test';
  }
};

// 添加CORS头部
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Max-Age': '86400',
};

// 处理OPTIONS预检请求
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: corsHeaders,
  });
}

export async function POST(request: NextRequest) {
  try {
    // 验证JWT令牌
    const userPayload = getCurrentUserFromRequest(request);
    if (!userPayload) {
      return NextResponse.json(
        { error: "未授权访问" },
        { status: 401, headers: corsHeaders }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const title = formData.get('title') as string || file?.name || '未命名视频';

    if (!file) {
      return NextResponse.json(
        { error: "未找到上传文件" },
        { status: 400, headers: corsHeaders }
      );
    }

    // 验证文件类型
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm'];
    const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];
    const fileExtension = file.name.toLowerCase().split('.').pop();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(`.${fileExtension}`)) {
      return NextResponse.json(
        { error: "不支持的文件类型。请上传MP4、AVI、MOV、MKV或WEBM格式的视频文件" },
        { status: 400, headers: corsHeaders }
      );
    }

    // 验证文件大小 (1GB限制)
    const maxSize = 1024 * 1024 * 1024; // 1GB = 1024MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: "文件大小不能超过1GB。如需上传更大文件，请联系管理员。" },
        { status: 400, headers: corsHeaders }
      );
    }

    const environment = getEnvironment();
    const storageBucket = getStorageBucket();
    
    console.log(`📤 Uploading file in ${environment} environment:`);
    console.log(`  - File: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`);
    console.log(`  - Bucket: ${storageBucket}`);

    // 生成唯一文件名
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 15);
    const safeFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
    const fileName = `${timestamp}_${randomStr}_${safeFileName}`;
    const filePath = `videos/${userPayload.sub}/${fileName}`;

    // 上传到Supabase Storage
    const fileBuffer = await file.arrayBuffer();
    const { data: uploadData, error: uploadError } = await supabaseServer.storage
      .from(storageBucket)
      .upload(filePath, fileBuffer, {
        contentType: file.type,
        duplex: 'half'
      });

    if (uploadError) {
      console.error('❌ Supabase Storage upload error:', uploadError);
      
      if (uploadError.message.includes('row-level security') || uploadError.message.includes('not found')) {
        return NextResponse.json(
          { error: `存储桶 "${storageBucket}" 不存在或配置错误。请先在 Supabase Dashboard 中创建存储桶。` },
          { status: 500, headers: corsHeaders }
        );
      }
      
      return NextResponse.json(
        { error: `文件上传失败: ${uploadError.message}` },
        { status: 500, headers: corsHeaders }
      );
    }

    // 获取文件公共URL
    const { data: urlData } = supabaseServer.storage
      .from(storageBucket)
      .getPublicUrl(filePath);

    console.log(`✅ File uploaded successfully to ${storageBucket}: ${uploadData.path}`);

    // 返回文件信息
    return NextResponse.json({
      message: "文件上传成功",
      video_id: `video_${timestamp}_${randomStr}`,
      file_path: uploadData.path,
      file_url: urlData.publicUrl,
      original_filename: file.name,
      file_size: file.size,
      title: title,
      upload_time: new Date().toISOString()
    }, { headers: corsHeaders });

  } catch (error) {
    console.error('❌ 文件上传错误:', error);
    
    if (error instanceof APIError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode, headers: corsHeaders }
      );
    }

    return NextResponse.json(
      { error: "文件上传失败，请稍后重试" },
      { status: 500, headers: corsHeaders }
    );
  }
} 