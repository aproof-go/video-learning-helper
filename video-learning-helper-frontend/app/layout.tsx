import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/contexts/auth-context"
import { Header } from "@/components/header"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "AI拉片助手 - 专业影视分析工具",
  description: "AI拉片助手为影视专业人士提供自动视频分割、转场检测、音频转写和报告生成服务",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <AuthProvider>
            <div className="flex min-h-screen flex-col">
              <Header />
              {children}
              <footer className="border-t py-6 md:py-0">
                <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
                  <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
                    © 2025 AI拉片助手. 保留所有权利.
                  </p>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <a href="#" className="transition-colors hover:text-foreground">
                      隐私政策
                    </a>
                    <a href="#" className="transition-colors hover:text-foreground">
                      使用条款
                    </a>
                    <a href="#" className="transition-colors hover:text-foreground">
                      联系我们
                    </a>
                  </div>
                </div>
              </footer>
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
