import Link from "next/link"
import { Button } from "@/components/ui/button"

export function Hero() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-white">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">AI拉片助手</h1>
              <p className="max-w-[600px] text-gray-500 md:text-xl">
                专业影视分析工具，一键完成视频分割、转场检测、音频转写和报告生成
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link href="#upload">
                <Button size="lg">开始分析</Button>
              </Link>
              <Link href="#features">
                <Button variant="outline" size="lg">
                  了解更多
                </Button>
              </Link>
            </div>
          </div>
          <div className="flex items-center justify-center">
            <div className="relative h-[350px] w-full overflow-hidden rounded-xl bg-gray-100">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-700 opacity-90"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="space-y-2 text-center text-white">
                  <div className="text-lg font-medium">专业影视分析</div>
                  <div className="text-4xl font-bold">AI拉片助手</div>
                  <div className="mx-auto mt-4 h-1 w-12 rounded-full bg-white"></div>
                  <div className="mt-4 text-sm">为影视专业人士打造的智能分析工具</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
