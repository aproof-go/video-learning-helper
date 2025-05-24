import { ForgotPasswordForm } from "@/components/forgot-password-form"
import type { Metadata } from "next"
import Link from "next/link"

export const metadata: Metadata = {
  title: "忘记密码 | AI拉片助手",
  description: "重置您的AI拉片助手账户密码",
}

export default function ForgotPasswordPage() {
  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">忘记密码</h1>
          <p className="text-sm text-muted-foreground">输入您的邮箱，我们将发送重置密码链接</p>
        </div>
        <ForgotPasswordForm />
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link href="/login" className="hover:text-brand underline underline-offset-4">
            返回登录
          </Link>
        </p>
      </div>
    </div>
  )
}
