"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react"

export function VerifyEmailForm({ token, email }: { token?: string; email?: string }) {
  const router = useRouter()
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")
  const [message, setMessage] = useState<string>("")
  const [countdown, setCountdown] = useState(5)

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token || !email) {
        setStatus("error")
        setMessage("验证链接无效，缺少必要参数")
        return
      }

      try {
        // 模拟API调用
        await new Promise((resolve) => setTimeout(resolve, 2000))

        // 这里应该是实际的验证邮箱API调用
        // const response = await fetch('/api/auth/verify-email', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ token, email }),
        // })

        // if (!response.ok) {
        //   throw new Error('邮箱验证失败，链接可能已过期')
        // }

        setStatus("success")
        setMessage("邮箱验证成功！")

        // 倒计时后自动跳转
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) {
              clearInterval(timer)
              router.push("/")
              return 0
            }
            return prev - 1
          })
        }, 1000)
      } catch (err) {
        setStatus("error")
        setMessage("邮箱验证失败，链接可能已过期")
      }
    }

    verifyEmail()
  }, [token, email, router])

  const resendVerification = async () => {
    if (!email) return

    setStatus("loading")
    setMessage("正在重新发送验证邮件...")

    try {
      // 模拟API调用
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // 这里应该是实际的重新发送验证邮件API调用
      // const response = await fetch('/api/auth/resend-verification', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email }),
      // })

      // if (!response.ok) {
      //   throw new Error('重新发送验证邮件失败')
      // }

      setStatus("success")
      setMessage("验证邮件已重新发送，请查收")
    } catch (err) {
      setStatus("error")
      setMessage("重新发送验证邮件失败，请稍后再试")
    }
  }

  return (
    <div className="grid gap-6">
      {status === "loading" && (
        <div className="flex flex-col items-center justify-center py-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-center">正在验证邮箱，请稍候...</p>
        </div>
      )}

      {status === "success" && (
        <Alert variant="default" className="border-green-500 text-green-500">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>
            {message}
            {countdown > 0 && <span> {countdown}秒后自动跳转...</span>}
          </AlertDescription>
        </Alert>
      )}

      {status === "error" && (
        <>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{message}</AlertDescription>
          </Alert>
          {email && (
            <Button onClick={resendVerification} className="w-full">
              重新发送验证邮件
            </Button>
          )}
        </>
      )}
    </div>
  )
}
