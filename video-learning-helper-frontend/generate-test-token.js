const jwt = require('jsonwebtoken');

// 使用默认的测试密钥
const JWT_SECRET = process.env.JWT_SECRET_KEY || 'your-secret-key';

// 创建测试token
const payload = {
  sub: 'test-user@example.com',  // 测试用户邮箱
  exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24) // 24小时后过期
};

const token = jwt.sign(payload, JWT_SECRET, { algorithm: 'HS256' });

console.log('🔑 测试 JWT Token:');
console.log(token);
console.log('');
console.log('📋 Token 信息:');
console.log('- 用户邮箱:', payload.sub);
console.log('- 过期时间:', new Date(payload.exp * 1000).toLocaleString());
console.log('- 密钥:', JWT_SECRET); 