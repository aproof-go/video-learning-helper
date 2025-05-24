import { Suspense } from "react"
import { VerifyEmailForm } from "@/components/verify-email-form"
import type { Metadata } from "next"
import Link from "next/link"

export const metadata: Metadata = {
  title: "验证邮箱 | AI拉片助手",
  description: "验证您的AI拉片助手账户邮箱",
}

export default async function VerifyEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string; email?: string }>
}) {
  const resolvedSearchParams = await searchParams
  const { token, email } = resolvedSearchParams

  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">验证邮箱</h1>
          <p className="text-sm text-muted-foreground">请验证您的邮箱地址以完成注册</p>
        </div>
        <Suspense
          fallback={
            <div className="flex justify-center">
              <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
            </div>
          }
        >
          <VerifyEmailForm token={token} email={email} />
        </Suspense>
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link href="/" className="hover:text-brand underline underline-offset-4">
            返回首页
          </Link>
        </p>
      </div>
    </div>
  )
}
