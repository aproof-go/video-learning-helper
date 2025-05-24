import { Upload } from "@/components/upload"
import { Features } from "@/components/features"
import { HowItWorks } from "@/components/how-it-works"
import { Hero } from "@/components/hero"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <Hero />
      <Features />
      <HowItWorks />
      <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-50">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">开始分析您的视频</h2>
              <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                上传您的视频文件，我们的AI将自动分析并生成报告
              </p>
            </div>
            <Upload />
          </div>
        </div>
      </section>
    </main>
  )
}
