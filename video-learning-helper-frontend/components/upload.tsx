"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { UploadIcon, X, Check, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/contexts/auth-context"
import { analysisApi, ApiError } from "@/lib/api"
import { createClient } from '@supabase/supabase-js'

// 环境检测函数
const getEnvironment = (): 'development' | 'production' => {
  if (typeof window !== 'undefined') {
    if (window.location.hostname.includes('vercel.app')) return 'production';
    if (window.location.hostname === 'localhost') return 'development';
  }
  return 'development';
};

// 获取 Supabase 配置
const getSupabaseConfig = () => {
  const environment = getEnvironment();
  
  switch (environment) {
    case 'production':
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL_PROD || process.env.NEXT_PUBLIC_SUPABASE_URL,
        anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY_PROD || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        bucket: 'video-learning-prod'
      };
    case 'development':
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL_DEV || process.env.NEXT_PUBLIC_SUPABASE_URL,
        anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY_DEV || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        bucket: 'video-learning-test'
      };
    default:
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL,
        anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        bucket: 'video-learning-test'
      };
  }
};

export function Upload() {
  const router = useRouter()
  const { user } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const [analysisOptions, setAnalysisOptions] = useState({
    videoSegmentation: true,
    transitionDetection: true,
    audioTranscription: true,
    reportGeneration: true,
  })
  const [error, setError] = useState<string | null>(null)
  const [videoId, setVideoId] = useState<string | null>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0]
      validateAndSetFile(droppedFile)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0])
    }
  }

  const validateAndSetFile = (file: File) => {
    setError(null)

    // Check file type
    const validTypes = ["video/mp4", "video/quicktime", "video/avi", "video/webm", "video/mkv"]
    if (!validTypes.includes(file.type)) {
      setError("请上传支持的视频格式：MP4、MOV、AVI、WebM、MKV")
      return
    }

    // Check file size (limit to 1GB)
    const maxSize = 1024 * 1024 * 1024 // 1GB
    if (file.size > maxSize) {
      setError("文件大小不能超过1GB")
      return
    }

    setFile(file)
    // 自动设置标题为文件名（去掉扩展名）
    if (!title) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "")
      setTitle(nameWithoutExt)
    }
  }

  const handleUpload = async () => {
    if (!file || !user) {
      setError("请先登录并选择文件")
      return
    }

    if (!title.trim()) {
      setError("请输入视频标题")
      return
    }

    setUploadStatus("uploading")
    setError(null)
    setUploadProgress(0)

    try {
      // 获取token
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error("请先登录")
      }

      // 获取 Supabase 配置
      const supabaseConfig = getSupabaseConfig()
      const supabase = createClient(supabaseConfig.url!, supabaseConfig.anonKey!)
      
      console.log(`📤 Direct upload to Supabase (${getEnvironment()}):`);
      console.log(`  - File: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`);
      console.log(`  - Bucket: ${supabaseConfig.bucket}`);

      // 生成唯一文件名
      const timestamp = Date.now();
      const randomStr = Math.random().toString(36).substring(2, 15);
      const safeFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
      const fileName = `${timestamp}_${randomStr}_${safeFileName}`;
      const filePath = `videos/${user.email}/${fileName}`;

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const newProgress = prev + Math.random() * 15;
          return newProgress >= 90 ? 90 : newProgress;
        });
      }, 500);

      // 直接上传到 Supabase Storage
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from(supabaseConfig.bucket)
        .upload(filePath, file, {
          contentType: file.type,
          duplex: 'half'
        });

      clearInterval(progressInterval);
      setUploadProgress(95);

      if (uploadError) {
        console.error('❌ Supabase Storage upload error:', uploadError);
        
        if (uploadError.message.includes('not found') || uploadError.message.includes('does not exist')) {
          throw new Error(`存储桶 "${supabaseConfig.bucket}" 不存在。请先在 Supabase Dashboard 中创建存储桶。`);
        }
        
        throw new Error(`文件上传失败: ${uploadError.message}`);
      }

      // 获取文件公共URL
      const { data: urlData } = supabase.storage
        .from(supabaseConfig.bucket)
        .getPublicUrl(filePath);

      console.log(`✅ File uploaded successfully to ${supabaseConfig.bucket}: ${uploadData.path}`);

      const generatedVideoId = `video_${timestamp}_${randomStr}`;
      setVideoId(generatedVideoId);
      setUploadProgress(100);

      // 创建分析任务
      console.log('🔍 About to create analysis task with data:', {
        video_id: generatedVideoId,
        video_segmentation: analysisOptions.videoSegmentation,
        transition_detection: analysisOptions.transitionDetection,
        audio_transcription: analysisOptions.audioTranscription,
        report_generation: analysisOptions.reportGeneration,
      });
      
      await analysisApi.createTask({
        video_id: generatedVideoId,
        video_segmentation: analysisOptions.videoSegmentation,
        transition_detection: analysisOptions.transitionDetection,
        audio_transcription: analysisOptions.audioTranscription,
        report_generation: analysisOptions.reportGeneration,
      }, token)

      setUploadStatus("success")

      // 跳转到分析页面
      setTimeout(() => {
        router.push(`/analysis/${generatedVideoId}`)
      }, 2000)

    } catch (err) {
      console.error('Upload error:', err)
      setUploadStatus("error")
      
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("登录已过期，请重新登录")
        } else if (err.status === 422) {
          setError(`数据验证失败: ${err.message}`)
        } else {
          setError(err.message)
        }
      } else if (err instanceof Error) {
        setError(err.message)
      } else {
        setError("上传失败，请稍后重试")
      }
    }
  }

  const handleOptionChange = (option: keyof typeof analysisOptions) => {
    setAnalysisOptions((prev) => ({
      ...prev,
      [option]: !prev[option],
    }))
  }

  const resetUpload = () => {
    setFile(null)
    setTitle("")
    setDescription("")
    setUploadProgress(0)
    setUploadStatus("idle")
    setError(null)
    setVideoId(null)
  }

  // 如果用户未登录，显示登录提示
  if (!user) {
    return (
      <div className="w-full max-w-3xl mx-auto">
        <Card className="w-full">
          <CardContent className="p-6">
            <div className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium mb-2">请先登录</h3>
              <p className="text-sm text-gray-500 mb-6">您需要登录后才能上传视频</p>
              <div className="flex gap-4">
                <Button onClick={() => router.push('/login')}>
                  登录
                </Button>
                <Button variant="outline" onClick={() => router.push('/register')}>
                  注册
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div id="upload" className="w-full max-w-3xl mx-auto">
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card className="w-full">
        <CardContent className="p-6">
          {uploadStatus === "idle" && (
            <>
              <div
                className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 transition-colors ${
                  isDragging ? "border-purple-500 bg-purple-50" : "border-gray-300"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {!file ? (
                  <>
                    <UploadIcon className="h-12 w-12 text-gray-400 mb-4" />
                    <p className="text-lg font-medium mb-1">拖拽文件到此处或点击上传</p>
                    <p className="text-sm text-gray-500 mb-4">支持MP4、MOV、AVI、WebM、MKV格式，最大1GB</p>
                    <Button onClick={() => document.getElementById("file-upload")?.click()}>选择文件</Button>
                    <input
                      id="file-upload"
                      type="file"
                      accept=".mp4,.mov,.avi,.webm,.mkv,video/*"
                      className="hidden"
                      onChange={handleFileChange}
                    />
                  </>
                ) : (
                  <div className="w-full">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded bg-purple-100 flex items-center justify-center mr-3">
                          <UploadIcon className="h-5 w-5 text-purple-600" />
                        </div>
                        <div>
                          <p className="font-medium truncate max-w-[200px] sm:max-w-[300px]">{file.name}</p>
                          <p className="text-sm text-gray-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon" onClick={resetUpload}>
                        <X className="h-5 w-5" />
                      </Button>
                    </div>

                    {/* 视频信息输入 */}
                    <div className="space-y-4 mb-6">
                      <div>
                        <Label htmlFor="title">视频标题 *</Label>
                        <Input
                          id="title"
                          value={title}
                          onChange={(e) => setTitle(e.target.value)}
                          placeholder="请输入视频标题"
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="description">视频描述</Label>
                        <Textarea
                          id="description"
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          placeholder="请输入视频描述（可选）"
                          className="mt-1"
                          rows={3}
                        />
                      </div>
                    </div>

                    <div className="space-y-4 mt-6">
                      <h3 className="text-lg font-medium">选择分析选项</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="videoSegmentation"
                            checked={analysisOptions.videoSegmentation}
                            onCheckedChange={() => handleOptionChange("videoSegmentation")}
                          />
                          <div className="grid gap-1.5">
                            <Label htmlFor="videoSegmentation">视频分割与GIF导出</Label>
                            <p className="text-sm text-gray-500">自动分割视频并导出GIF</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="transitionDetection"
                            checked={analysisOptions.transitionDetection}
                            onCheckedChange={() => handleOptionChange("transitionDetection")}
                          />
                          <div className="grid gap-1.5">
                            <Label htmlFor="transitionDetection">转场检测与标注</Label>
                            <p className="text-sm text-gray-500">识别各类转场类型</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="audioTranscription"
                            checked={analysisOptions.audioTranscription}
                            onCheckedChange={() => handleOptionChange("audioTranscription")}
                          />
                          <div className="grid gap-1.5">
                            <Label htmlFor="audioTranscription">音频转写</Label>
                            <p className="text-sm text-gray-500">转写音轨为字幕文本</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="reportGeneration"
                            checked={analysisOptions.reportGeneration}
                            onCheckedChange={() => handleOptionChange("reportGeneration")}
                          />
                          <div className="grid gap-1.5">
                            <Label htmlFor="reportGeneration">分析报告生成</Label>
                            <p className="text-sm text-gray-500">生成结构化PDF分析报告</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Button 
                      className="w-full mt-6" 
                      onClick={handleUpload}
                      disabled={!title.trim()}
                    >
                      开始分析
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}

          {uploadStatus === "uploading" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">上传中...</h3>
                <p className="text-sm font-medium">{Math.round(uploadProgress)}%</p>
              </div>
              <Progress value={uploadProgress} className="h-2" />
              <p className="text-sm text-gray-500">正在上传视频，请勿关闭页面...</p>
            </div>
          )}

          {uploadStatus === "success" && (
            <div className="flex flex-col items-center justify-center py-6">
              <div className="rounded-full bg-green-100 p-3 mb-4">
                <Check className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-medium mb-2">上传成功</h3>
              <p className="text-sm text-gray-500 mb-6">视频已成功上传，正在跳转到分析页面...</p>
              <Progress value={100} className="h-2 w-full" />
            </div>
          )}

          {uploadStatus === "error" && (
            <div className="flex flex-col items-center justify-center py-6">
              <div className="rounded-full bg-red-100 p-3 mb-4">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
              <h3 className="text-xl font-medium mb-2">上传失败</h3>
              <p className="text-sm text-gray-500 mb-6">请检查网络连接后重试</p>
              <Button onClick={resetUpload}>重新上传</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
