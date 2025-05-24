import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // 简单的健康检查
    const health = {
      status: "healthy",
      version: "2.0.0",
      platform: "vercel",
      timestamp: new Date().toISOString(),
      database: "supabase"
    };

    return NextResponse.json(health, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { status: "unhealthy", error: "Health check failed" },
      { status: 500 }
    );
  }
} 