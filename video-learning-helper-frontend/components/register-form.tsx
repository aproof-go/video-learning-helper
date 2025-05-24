"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { authApi, ApiError } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

const formSchema = z
  .object({
    name: z.string().min(2, {
      message: "姓名至少需要2个字符",
    }),
    email: z.string().email({
      message: "请输入有效的邮箱地址",
    }),
    password: z.string().min(6, {
      message: "密码至少需要6个字符",
    }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "两次输入的密码不一致",
    path: ["confirmPassword"],
  })

export function RegisterForm() {
  const router = useRouter()
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [autoLogin, setAutoLogin] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      // 调用真实的注册API
      const response = await authApi.register({
        email: values.email,
        password: values.password,
        name: values.name,
      })

      // 注册成功
      setSuccess(`注册成功！欢迎您，${response.name || response.email}！正在为您自动登录...`)

      // 清空表单
      form.reset()

      // 自动登录
      setAutoLogin(true)
      
      try {
        // 使用注册时的密码自动登录
        const loginResponse = await authApi.login({
          email: values.email,
          password: values.password,
        })

        // 使用认证上下文的login方法
        await login(loginResponse.access_token)

        // 延迟跳转到首页
        setTimeout(() => {
          router.push("/")
        }, 2000)
      } catch (loginError) {
        // 自动登录失败，跳转到登录页面
        setSuccess(`注册成功！请前往登录页面登录您的账户。`)
        setTimeout(() => {
          router.push("/login")
        }, 3000)
      }
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 400) {
          setError("该邮箱已被注册，请使用其他邮箱或直接登录")
        } else if (err.status === 422) {
          setError("输入信息格式不正确，请检查邮箱格式")
        } else {
          setError(err.message)
        }
      } else {
        setError("注册失败，请稍后再试")
      }
    } finally {
      setIsLoading(false)
      setAutoLogin(false)
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

      {success && (
        <Alert variant="default" className="border-green-500 text-green-500">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>姓名</FormLabel>
                <FormControl>
                  <Input placeholder="张三" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
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
            control={form.control}
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
          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>确认密码</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="••••••••" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isLoading || autoLogin}>
            {autoLogin ? "正在登录..." : isLoading ? "注册中..." : "注册"}
          </Button>
        </form>
      </Form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">或者</span>
        </div>
      </div>

      <Button variant="outline" type="button" disabled={isLoading || autoLogin}>
        使用微信注册
      </Button>
    </div>
  )
}
