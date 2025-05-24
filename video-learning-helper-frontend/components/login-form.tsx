"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { authApi, ApiError } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

// 修改 formSchema 为两个不同的 schema
const passwordFormSchema = z.object({
  email: z.string().email({
    message: "请输入有效的邮箱地址",
  }),
  password: z.string().min(6, {
    message: "密码至少需要6个字符",
  }),
})

const verificationCodeFormSchema = z.object({
  phone: z.string().regex(/^1[3-9]\d{9}$/, {
    message: "请输入有效的手机号码",
  }),
  code: z.string().length(6, {
    message: "验证码应为6位数字",
  }),
})

// 替换整个 LoginForm 函数
export function LoginForm() {
  const router = useRouter()
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSendingCode, setIsSendingCode] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [loginMethod, setLoginMethod] = useState<"password" | "verification">("password")

  const passwordForm = useForm<z.infer<typeof passwordFormSchema>>({
    resolver: zodResolver(passwordFormSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  const verificationForm = useForm<z.infer<typeof verificationCodeFormSchema>>({
    resolver: zodResolver(verificationCodeFormSchema),
    defaultValues: {
      phone: "",
      code: "",
    },
  })

  // 处理密码登录提交
  async function onPasswordSubmit(values: z.infer<typeof passwordFormSchema>) {
    setIsLoading(true)
    setError(null)

    try {
      // 调用真实的登录API
      const response = await authApi.login({
        email: values.email,
        password: values.password,
      })

      // 使用认证上下文的login方法
      await login(response.access_token)

      // 登录成功，重定向到首页
      router.push("/")
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("邮箱或密码错误，请检查后重试")
        } else if (err.status === 422) {
          setError("输入信息格式不正确，请检查邮箱格式")
        } else {
          setError(err.message)
        }
      } else {
        setError("登录失败，请检查网络连接")
      }
    } finally {
      setIsLoading(false)
    }
  }

  // 处理验证码登录提交
  async function onVerificationSubmit(values: z.infer<typeof verificationCodeFormSchema>) {
    setIsLoading(true)
    setError(null)

    try {
      // 模拟API调用 - 验证码登录暂未实现
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // 这里应该是实际的验证码登录API调用
      // const response = await fetch('/api/auth/login/verification', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(values),
      // })

      // if (!response.ok) {
      //   throw new Error('验证码登录失败，请检查您的手机号和验证码')
      // }

      // 登录成功，重定向到首页
      router.push("/")
    } catch (err) {
      // 在实际应用中，这里应该处理API返回的错误
      setError("验证码登录功能暂未开放，请使用邮箱密码登录")
    } finally {
      setIsLoading(false)
    }
  }

  // 发送验证码
  async function sendVerificationCode() {
    const phone = verificationForm.getValues("phone")
    const phoneResult = verificationCodeFormSchema.shape.phone.safeParse(phone)

    if (!phoneResult.success) {
      verificationForm.setError("phone", {
        type: "manual",
        message: "请输入有效的手机号码",
      })
      return
    }

    setIsSendingCode(true)

    try {
      // 模拟API调用
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // 这里应该是实际的发送验证码API调用
      // const response = await fetch('/api/auth/send-code', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ phone }),
      // })

      // if (!response.ok) {
      //   throw new Error('发送验证码失败')
      // }

      // 开始倒计时
      setCountdown(60)
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } catch (err) {
      setError("验证码功能暂未开放")
    } finally {
      setIsSendingCode(false)
    }
  }

  return (
    <div className="grid gap-6">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="password" onValueChange={(value) => setLoginMethod(value as "password" | "verification")}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="password">密码登录</TabsTrigger>
          <TabsTrigger value="verification">验证码登录</TabsTrigger>
        </TabsList>

        <TabsContent value="password">
          <Form {...passwordForm}>
            <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
              <FormField
                control={passwordForm.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>邮箱</FormLabel>
                    <FormControl>
                      <Input placeholder="your@email.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={passwordForm.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>密码</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex items-center justify-between">
                <Link href="/forgot-password" className="text-sm text-muted-foreground hover:text-primary">
                  忘记密码？
                </Link>
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "登录中..." : "登录"}
              </Button>
            </form>
          </Form>
        </TabsContent>

        <TabsContent value="verification">
          <Form {...verificationForm}>
            <form onSubmit={verificationForm.handleSubmit(onVerificationSubmit)} className="space-y-4">
              <FormField
                control={verificationForm.control}
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>手机号</FormLabel>
                    <FormControl>
                      <Input placeholder="请输入手机号" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={verificationForm.control}
                name="code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>验证码</FormLabel>
                    <div className="flex space-x-2">
                      <FormControl>
                        <Input placeholder="请输入验证码" {...field} />
                      </FormControl>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={sendVerificationCode}
                        disabled={isSendingCode || countdown > 0}
                        className="whitespace-nowrap"
                      >
                        {countdown > 0 ? `${countdown}s` : isSendingCode ? "发送中..." : "发送验证码"}
                      </Button>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "登录中..." : "验证码登录"}
              </Button>
            </form>
          </Form>
        </TabsContent>
      </Tabs>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">或者</span>
        </div>
      </div>

      <Button variant="outline" type="button" disabled={isLoading}>
        使用微信登录
      </Button>
    </div>
  )
}
