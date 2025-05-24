import { LoginForm } from "@/components/login-form"
import type { Metadata } from "next"
import Link from "next/link"

export const metadata: Metadata = {
  title: "登录 | AI拉片助手",
  description: "登录您的AI拉片助手账户",
}

export default function LoginPage() {
  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">登录账户</h1>
          <p className="text-sm text-muted-foreground">输入您的邮箱和密码登录</p>
        </div>
        <LoginForm />
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link href="/register" className="hover:text-brand underline underline-offset-4">
            没有账户？注册
          </Link>
        </p>
      </div>
    </div>
  )
}
