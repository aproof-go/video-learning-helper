import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { NextRequest } from 'next/server';

const JWT_SECRET = process.env.JWT_SECRET_KEY || 'your-secret-key';
const ALGORITHM = 'HS256';

export interface UserPayload {
  sub: string; // email
  exp: number;
}

// 创建访问令牌
export function createAccessToken(email: string): string {
  const payload: UserPayload = {
    sub: email,
    exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24) // 24小时
  };
  
  return jwt.sign(payload, JWT_SECRET, { algorithm: ALGORITHM });
}

// 验证访问令牌
export function verifyAccessToken(token: string): UserPayload | null {
  try {
    const payload = jwt.verify(token, JWT_SECRET, { algorithms: [ALGORITHM] }) as UserPayload;
    return payload;
  } catch (error) {
    return null;
  }
}

// 密码哈希
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

// 验证密码
export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword);
}

// 从请求中获取当前用户
export function getCurrentUserFromRequest(request: NextRequest): UserPayload | null {
  const authHeader = request.headers.get('authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }
  
  const token = authHeader.substring(7);
  return verifyAccessToken(token);
}

// API错误响应
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number = 400,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
} 