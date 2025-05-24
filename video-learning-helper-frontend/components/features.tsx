import { Film, Scissors, FileText, Mic, Clock, Download, Shield, Zap } from "lucide-react"

export function Features() {
  return (
    <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-white">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <div className="inline-block rounded-lg bg-gray-100 px-3 py-1 text-sm">核心功能</div>
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">专业影视分析工具</h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
              AI拉片助手为影视专业人士提供全方位的视频分析服务
            </p>
          </div>
        </div>
        <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 py-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-purple-100 p-3">
              <Scissors className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold">视频分割</h3>
            <p className="text-center text-sm text-gray-500">自动识别转场并分割视频片段，导出GIF动图</p>
          </div>
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-purple-100 p-3">
              <Film className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold">转场检测</h3>
            <p className="text-center text-sm text-gray-500">自动识别各类转场类型，提供转场密度统计</p>
          </div>
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-purple-100 p-3">
              <Mic className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold">音频转写</h3>
            <p className="text-center text-sm text-gray-500">自动分离人声与背景音乐，转写为高准确率字幕</p>
          </div>
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-purple-100 p-3">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold">分析报告</h3>
            <p className="text-center text-sm text-gray-500">生成结构化PDF分析报告，包含片段集、转场统计等</p>
          </div>
        </div>
        <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-gray-100 p-3">
              <Clock className="h-6 w-6 text-gray-600" />
            </div>
            <h3 className="text-xl font-bold">高效分析</h3>
            <p className="text-center text-sm text-gray-500">2小时影片分析用时低于20分钟</p>
          </div>
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-gray-100 p-3">
              <Download className="h-6 w-6 text-gray-600" />
            </div>
            <h3 className="text-xl font-bold">一键导出</h3>
            <p className="text-center text-sm text-gray-500">支持GIF、PDF报告和字幕文件导出</p>
          </div>
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-gray-100 p-3">
              <Shield className="h-6 w-6 text-gray-600" />
            </div>
            <h3 className="text-xl font-bold">数据安全</h3>
            <p className="text-center text-sm text-gray-500">用户数据隐私与影片版权有明确保障</p>
          </div>
          <div className="flex flex-col items-center space-y-2 rounded-lg border p-6 shadow-sm">
            <div className="rounded-full bg-gray-100 p-3">
              <Zap className="h-6 w-6 text-gray-600" />
            </div>
            <h3 className="text-xl font-bold">极简操作</h3>
            <p className="text-center text-sm text-gray-500">界面简洁，上手零门槛，分析进度可视</p>
          </div>
        </div>
      </div>
    </section>
  )
}
