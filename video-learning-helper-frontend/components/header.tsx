'use client'

import Link from 'next/link'
import { useAuth } from '@/contexts/auth-context'
import { UserMenu } from '@/components/user-menu'

export function Header() {
  const { user, isLoading } = useAuth()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="flex items-center space-x-2">
            <span className="font-bold text-xl">AI拉片助手</span>
          </Link>
        </div>
        <nav className="flex items-center space-x-4 lg:space-x-6 mx-6">
          <Link href="/" className="text-sm font-medium transition-colors hover:text-primary">
            首页
          </Link>
          {user && (
            <Link
              href="/videos"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
            >
              我的视频
            </Link>
          )}
          <Link
            href="#features"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
          >
            功能
          </Link>
          <Link
            href="#upload"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
          >
            上传
          </Link>
        </nav>
        <div className="ml-auto flex items-center space-x-4">
          {isLoading ? (
            // 加载状态
            <div className="h-8 w-16 animate-pulse rounded bg-muted"></div>
          ) : user ? (
            // 已登录状态 - 显示用户菜单
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                欢迎，{user.name || user.email.split('@')[0]}
              </span>
              <UserMenu />
            </div>
          ) : (
            // 未登录状态 - 显示登录注册按钮
            <>
              <Link
                href="/login"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
              >
                登录
              </Link>
              <Link
                href="/register"
                className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
              >
                注册
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
} 