"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { videoApi, analysisApi, BACKEND_BASE_URL, VideoResponse, AnalysisTaskResponse, ApiError } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { 
  Play, 
  Download, 
  RefreshCw, 
  Clock, 
  FileVideo, 
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2,
  ArrowLeft
} from "lucide-react"
import { AnalysisResult } from "@/components/analysis-result"

export default function AnalysisPage() {
  const router = useRouter()
  const params = useParams()
  const { user } = useAuth()
  const videoId = params.id as string

  const [video, setVideo] = useState<VideoResponse | null>(null)
  const [tasks, setTasks] = useState<AnalysisTaskResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [showReanalysisDialog, setShowReanalysisDialog] = useState(false)
  const [reanalysisConfig, setReanalysisConfig] = useState({
    video_segmentation: true,
    transition_detection: true,
    audio_transcription: false,
    report_generation: false
  })
  const [isCreatingTask, setIsCreatingTask] = useState(false)

  useEffect(() => {
    if (user && videoId) {
      loadData()
    }
  }, [user, videoId])

  const loadData = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error("请先登录")
      }

      // 并行加载视频信息和分析任务
      const [videoData, tasksData] = await Promise.all([
        videoApi.getVideo(videoId, token),
        analysisApi.getVideoTasks(videoId, token)
      ])

      setVideo(videoData)
      setTasks(tasksData)
    } catch (err) {
      console.error('Failed to load analysis data:', err)
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("登录已过期，请重新登录")
        } else if (err.status === 404) {
          setError("视频不存在")
        } else if (err.status === 403) {
          setError("无权访问此视频")
        } else {
          setError(err.message)
        }
      } else {
        setError("加载失败，请稍后重试")
      }
    } finally {
      setLoading(false)
    }
  }

  const refreshData = async () => {
    setRefreshing(true)
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) return

      const tasksData = await analysisApi.getVideoTasks(videoId, token)
      setTasks(tasksData)
    } catch (err) {
      console.error('Failed to refresh data:', err)
    } finally {
      setRefreshing(false)
    }
  }

  const handleReanalysis = async () => {
    setIsCreatingTask(true)
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error("请先登录")
      }

      // 创建新的分析任务
      const taskData = {
        video_id: videoId,
        ...reanalysisConfig
      }

      const newTask = await analysisApi.createTask(taskData, token)
      console.log('🎉 重新分析任务已创建:', newTask.id)

      // 关闭对话框
      setShowReanalysisDialog(false)

      // 刷新任务列表
      await refreshData()

      // 显示成功消息（这里可以添加toast通知）
      alert(`重新分析任务已创建！任务ID: ${newTask.id.slice(-8)}`)

    } catch (err) {
      console.error('Failed to create reanalysis task:', err)
      let errorMessage = "创建分析任务失败，请稍后重试"
      
      if (err instanceof Error) {
        errorMessage = err.message
      }
      
      alert(`错误: ${errorMessage}`)
    } finally {
      setIsCreatingTask(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'processing':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary">等待中</Badge>
      case 'processing':
        return <Badge variant="default">处理中</Badge>
      case 'completed':
        return <Badge variant="default" className="bg-green-500">已完成</Badge>
      case 'failed':
        return <Badge variant="destructive">失败</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '未知'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <AlertCircle className="h-12 w-12 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">请先登录</h2>
          <p className="text-gray-500 mb-6">您需要登录后才能查看分析结果</p>
          <div className="flex gap-4">
            <Button onClick={() => router.push('/login')}>
              登录
            </Button>
            <Button variant="outline" onClick={() => router.push('/register')}>
              注册
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-500">加载中...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold mb-2">加载失败</h2>
          <p className="text-gray-500 mb-6">{error}</p>
          <div className="flex gap-4">
            <Button onClick={() => router.push('/videos')}>
              返回视频列表
            </Button>
            <Button variant="outline" onClick={loadData}>
              重试
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (!video) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <FileVideo className="h-12 w-12 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">视频不存在</h2>
          <p className="text-gray-500 mb-6">请检查视频ID是否正确</p>
          <Button onClick={() => router.push('/videos')}>
            返回视频列表
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 头部导航 */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/videos')}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{video.title}</h1>
            <p className="text-gray-500 mt-1">视频分析结果</p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={refreshData}
          disabled={refreshing}
        >
          {refreshing ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          刷新
        </Button>
      </div>

      {/* 视频信息卡片 */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileVideo className="h-5 w-5" />
            <span>视频信息</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span className="text-sm text-gray-500">文件名:</span>
              <p className="font-medium">{video.filename}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">大小:</span>
              <p className="font-medium">{formatFileSize(video.file_size)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">时长:</span>
              <p className="font-medium">{formatDuration(video.duration)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">格式:</span>
              <p className="font-medium uppercase">{video.format || '未知'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">分辨率:</span>
              <p className="font-medium">
                {video.resolution_width && video.resolution_height 
                  ? `${video.resolution_width}x${video.resolution_height}`
                  : '未知'
                }
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-500">状态:</span>
              <div className="font-medium">{getStatusBadge(video.status)}</div>
            </div>
            <div>
              <span className="text-sm text-gray-500">上传时间:</span>
              <p className="font-medium">{new Date(video.created_at).toLocaleString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 分析任务 */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>分析任务</span>
            <div className="flex items-center space-x-4">
              <span className="text-sm font-normal text-gray-500">
                {tasks.length} 个任务
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowReanalysisDialog(true)}
                className="ml-4"
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                重新分析
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {tasks.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">暂无分析任务</p>
            </div>
          ) : (
            <div className="space-y-4">
              {tasks.map((task) => (
                <Card key={task.id} className="border-l-4 border-l-blue-500">
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(task.status)}
                        <span className="font-medium">
                          分析任务 #{task.id.slice(-8)}
                        </span>
                      </div>
                      {getStatusBadge(task.status)}
                    </div>

                    {/* 任务配置 */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">视频分割:</span>
                        <span className={task.video_segmentation ? "text-green-600" : "text-gray-400"}>
                          {task.video_segmentation ? "✓" : "✗"}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">转场检测:</span>
                        <span className={task.transition_detection ? "text-green-600" : "text-gray-400"}>
                          {task.transition_detection ? "✓" : "✗"}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">音频转写:</span>
                        <span className={task.audio_transcription ? "text-green-600" : "text-gray-400"}>
                          {task.audio_transcription ? "✓" : "✗"}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">报告生成:</span>
                        <span className={task.report_generation ? "text-green-600" : "text-gray-400"}>
                          {task.report_generation ? "✓" : "✗"}
                        </span>
                      </div>
                    </div>

                    {/* 时间信息 */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-500">
                      <div>
                        <span>创建时间:</span>
                        <span className="ml-1">{new Date(task.created_at).toLocaleString()}</span>
                      </div>
                      {task.started_at && (
                        <div>
                          <span>开始时间:</span>
                          <span className="ml-1">{new Date(task.started_at).toLocaleString()}</span>
                        </div>
                      )}
                      {task.completed_at && (
                        <div>
                          <span>完成时间:</span>
                          <span className="ml-1">{new Date(task.completed_at).toLocaleString()}</span>
                        </div>
                      )}
                    </div>

                    {/* 错误信息 */}
                    {task.error_message && (
                      <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{task.error_message}</AlertDescription>
                      </Alert>
                    )}

                    {/* 下载链接 */}
                    {task.status === 'completed' && (
                      <div className="flex gap-2 mt-4">
                        {task.report_pdf_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(`${BACKEND_BASE_URL}${task.report_pdf_url}`, '_blank')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            下载报告
                          </Button>
                        )}
                        {task.subtitle_srt_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(`${BACKEND_BASE_URL}${task.subtitle_srt_url}`, '_blank')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            下载字幕(SRT)
                          </Button>
                        )}
                        {task.subtitle_vtt_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(`${BACKEND_BASE_URL}${task.subtitle_vtt_url}`, '_blank')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            下载字幕(VTT)
                          </Button>
                        )}
                        {task.script_md_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(`${BACKEND_BASE_URL}${task.script_md_url}`, '_blank')}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            下载脚本(MD)
                          </Button>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 分析结果展示区域 */}
      {tasks.some(task => task.status === 'completed') && (
        <AnalysisResult id={videoId} />
      )}

      {/* 重新分析对话框 */}
      <Dialog open={showReanalysisDialog} onOpenChange={setShowReanalysisDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>重新分析视频</DialogTitle>
            <DialogDescription>
              为视频 "{video?.filename}" 创建新的分析任务
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="video_segmentation"
                  checked={reanalysisConfig.video_segmentation}
                  onCheckedChange={(checked) => 
                    setReanalysisConfig(prev => ({ ...prev, video_segmentation: !!checked }))
                  }
                />
                <label htmlFor="video_segmentation" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  视频分割 (AI智能场景分割)
                </label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="transition_detection"
                  checked={reanalysisConfig.transition_detection}
                  onCheckedChange={(checked) => 
                    setReanalysisConfig(prev => ({ ...prev, transition_detection: !!checked }))
                  }
                />
                <label htmlFor="transition_detection" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  转场检测 (画面变化分析)
                </label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="audio_transcription"
                  checked={reanalysisConfig.audio_transcription}
                  onCheckedChange={(checked) => 
                    setReanalysisConfig(prev => ({ ...prev, audio_transcription: !!checked }))
                  }
                />
                <label htmlFor="audio_transcription" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  音频转录 (语音识别转文字)
                </label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="report_generation"
                  checked={reanalysisConfig.report_generation}
                  onCheckedChange={(checked) => 
                    setReanalysisConfig(prev => ({ ...prev, report_generation: !!checked }))
                  }
                />
                <label htmlFor="report_generation" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  报告生成 (分析总结报告)
                </label>
              </div>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                💡 <strong>推荐配置：</strong> 启用"视频分割"和"转场检测"以获得最佳的AI智能分析结果
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowReanalysisDialog(false)}
              disabled={isCreatingTask}
            >
              取消
            </Button>
            <Button
              onClick={handleReanalysis}
              disabled={isCreatingTask || (!reanalysisConfig.video_segmentation && !reanalysisConfig.transition_detection && !reanalysisConfig.audio_transcription && !reanalysisConfig.report_generation)}
            >
              {isCreatingTask ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  创建中...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  开始分析
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
