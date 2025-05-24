/** @type {import('next').NextConfig} */
const nextConfig = {
  // 开发模式优化
  experimental: {
    // 启用 Turbopack (更快的开发服务器)
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
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

  // 开发服务器配置
  devIndicators: {
    buildActivity: true,
    buildActivityPosition: 'bottom-right',
  },

  // 编译优化
  swcMinify: true,
  
  // 图片优化
  images: {
    domains: ['localhost', '127.0.0.1'],
    unoptimized: process.env.NODE_ENV === 'development',
  },

  // API路由配置
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },

  // 环境变量
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
    FRONTEND_URL: process.env.FRONTEND_URL || 'http://localhost:3000',
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