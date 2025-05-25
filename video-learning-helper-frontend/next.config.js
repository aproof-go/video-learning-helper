/** @type {import('next').NextConfig} */
const nextConfig = {
  // 实验性功能（针对Next.js 15优化）
  experimental: {
    // 移除deprecated的turbo配置
  },

  // 热更新配置
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // 开发模式下的热更新优化
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
        ignored: ['**/node_modules', '**/.git', '**/.next'],
      }
    }
    return config
  },

  // 开发服务器配置（修复Next.js 15兼容性）
  devIndicators: {
    position: 'bottom-left', // 修复: 使用position替代已废弃的buildActivityPosition
  },

  // 移除已废弃的swcMinify配置
  
  // 图片优化
  images: {
    domains: ['localhost', '127.0.0.1', 'tjxqzmrmybrcmkflaimq.supabase.co'],
    unoptimized: process.env.NODE_ENV === 'development',
  },

  // 移除API重写规则 - 使用纯Next.js API Routes
  
  // 环境变量
  env: {
    FRONTEND_URL: process.env.FRONTEND_URL || (process.env.NODE_ENV === 'production' ? process.env.VERCEL_URL : 'http://localhost:3000'),
  },

  // 输出配置
  output: 'standalone',
  
  // 压缩配置
  compress: true,
  
  // 性能优化
  poweredByHeader: false,
  
  // 开发模式下的设置
  ...(process.env.NODE_ENV === 'development' && {
    typescript: {
      ignoreBuildErrors: false,
    },
    eslint: {
      ignoreDuringBuilds: false,
    },
  }),
}

module.exports = nextConfig 