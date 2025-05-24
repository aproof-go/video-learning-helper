import { RegisterForm } from "@/components/register-form"
import type { Metadata } from "next"
import Link from "next/link"

export const metadata: Metadata = {
  title: "注册 | AI拉片助手",
  description: "创建您的AI拉片助手账户",
}

export default function RegisterPage() {
  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">创建账户</h1>
          <p className="text-sm text-muted-foreground">填写以下信息创建您的账户</p>
        </div>
        <RegisterForm />
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link href="/login" className="hover:text-brand underline underline-offset-4">
            已有账户？登录
          </Link>
        </p>
      </div>
    </div>
  )
}
