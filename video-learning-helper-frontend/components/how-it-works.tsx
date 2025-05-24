export function HowItWorks() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-50">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <div className="inline-block rounded-lg bg-gray-100 px-3 py-1 text-sm">使用流程</div>
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">简单四步，完成分析</h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
              AI拉片助手让影视分析变得简单高效
            </p>
          </div>
        </div>
        <div className="mx-auto grid max-w-5xl grid-cols-1 gap-8 py-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col items-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
              <span className="text-2xl font-bold text-purple-600">1</span>
            </div>
            <h3 className="text-xl font-bold">上传视频</h3>
            <p className="text-center text-sm text-gray-500">选择本地视频文件上传，支持主流视频格式（.mp4/.mov）</p>
          </div>
          <div className="flex flex-col items-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
              <span className="text-2xl font-bold text-purple-600">2</span>
            </div>
            <h3 className="text-xl font-bold">选择分析项</h3>
            <p className="text-center text-sm text-gray-500">勾选需要的分析功能，如视频分割、音频转写、报告生成等</p>
          </div>
          <div className="flex flex-col items-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
              <span className="text-2xl font-bold text-purple-600">3</span>
            </div>
            <h3 className="text-xl font-bold">AI分析</h3>
            <p className="text-center text-sm text-gray-500">系统自动进行分析，实时显示进度，完成后自动跳转结果页</p>
          </div>
          <div className="flex flex-col items-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
              <span className="text-2xl font-bold text-purple-600">4</span>
            </div>
            <h3 className="text-xl font-bold">查看与导出</h3>
            <p className="text-center text-sm text-gray-500">预览分析结果，一键下载GIF、PDF报告和字幕文件</p>
          </div>
        </div>
      </div>
    </section>
  )
}
