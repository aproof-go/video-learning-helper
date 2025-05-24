import { NextResponse } from 'next/server';

// 添加CORS头部
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Max-Age': '86400',
};

// 处理OPTIONS预检请求
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: corsHeaders,
  });
}

export async function GET() {
  try {
    // 简单的健康检查 - Updated for Vercel deployment
    const health = {
      status: "healthy",
      version: "2.0.1",
      platform: "vercel",
      timestamp: new Date().toISOString(),
      database: "supabase"
    };

    return NextResponse.json(health, { status: 200, headers: corsHeaders });
  } catch (error) {
    return NextResponse.json(
      { status: "unhealthy", error: "Health check failed" },
      { status: 500, headers: corsHeaders }
    );
  }
} 