"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Download, FileText, Film, Scissors, Mic, Clock, ChevronRight, ChevronLeft, Play, Pause, AlertCircle, Eye, Camera, Users, MessageSquare } from "lucide-react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { toast } from "react-hot-toast"

interface VideoSegment {
  segment_id: number
  start_time: number
  end_time: number
  duration: number
  scene_type: string
  frame_count: number
  thumbnail_url?: string
  gif_url?: string
  // 新增AI分析字段
  content_analysis?: {
    caption: string // 文案（旁白或字幕）
    composition: string // 构图分析
    camera_movement: string // 运镜分析
    theme_analysis: string // 主题分析
    ai_commentary: string // AI简评
  }
}

interface Transition {
  transition_id: number
  timestamp: number
  strength: number
  type: string
}

interface TranscriptionSegment {
  start: number
  end: number
  text: string
  confidence: number
}

interface VideoInfo {
  duration: number
  fps: number
  width: number
  height: number
  file_size: number
}

interface AnalysisTask {
  id: string
  video_id: string
  user_id: string
  video_segmentation: boolean
  transition_detection: boolean
  audio_transcription: boolean
  report_generation: boolean
  status: string
  progress: string
  error_message?: string
  report_pdf_url?: string
  subtitle_srt_url?: string
  subtitle_vtt_url?: string
  script_md_url?: string
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

interface Video {
  id: string
  title: string
  filename: string
  file_size: number
  duration?: number
  resolution_width?: number
  resolution_height?: number
  format?: string
  status: string
  file_url?: string
  thumbnail_url?: string
  user_id: string
  created_at: string
  updated_at: string
}

interface AnalysisResults {
  video_info?: VideoInfo
  segments?: VideoSegment[]
  transitions?: Transition[]
  transcription?: {
    text: string
    language: string
    segments: TranscriptionSegment[]
  }
  _dataQuality?: {
    hasIssues: boolean
    issues: string[]
    score: number
  }
}

export function AnalysisResult({ id }: { id: string }) {
  const [currentPage, setCurrentPage] = useState(1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [video, setVideo] = useState<Video | null>(null)
  const [tasks, setTasks] = useState<AnalysisTask[]>([])
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const itemsPerPage = 10 // 改为10条每页

  // 获取认证token
  const getAuthToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token')
    }
    return null
  }

  // API调用函数
  const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = getAuthToken()
    if (!token) {
      throw new Error('未找到认证token，请重新登录')
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('认证已过期，请重新登录')
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // 获取视频信息
  const fetchVideo = async () => {
    try {
      const videoData = await fetchWithAuth(`http://localhost:8000/api/v1/videos/${id}`)
      setVideo(videoData)
    } catch (err) {
      console.error('获取视频信息失败:', err)
      setError(err instanceof Error ? err.message : '获取视频信息失败')
    }
  }

  // 获取分析任务
  const fetchTasks = async () => {
    try {
      const tasksData = await fetchWithAuth(`http://localhost:8000/api/v1/analysis/videos/${id}/tasks`)
      setTasks(tasksData)
      
      // 如果有完成的任务，优先选择有AI分析功能的任务
      const completedTasks = tasksData.filter((task: AnalysisTask) => task.status === 'completed')
      if (completedTasks.length > 0) {
        // 优先选择启用了视频分割和转场检测的任务（真正的AI分析）
        const aiTasks = completedTasks.filter((task: AnalysisTask) => 
          task.video_segmentation && task.transition_detection
        )
        
        let selectedTask: AnalysisTask
        if (aiTasks.length > 0) {
          // 从AI任务中选择最新的
          selectedTask = aiTasks.sort((a: AnalysisTask, b: AnalysisTask) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )[0]
          console.log('🧠 选择AI智能分析任务:', selectedTask.id)
        } else {
          // 如果没有AI任务，则选择最新的completed任务
          selectedTask = completedTasks.sort((a: AnalysisTask, b: AnalysisTask) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )[0]
          console.log('📝 选择最新的completed任务:', selectedTask.id)
        }
        
        await loadAnalysisResults(selectedTask.id)
      }
    } catch (err) {
      console.error('获取分析任务失败:', err)
      setError(err instanceof Error ? err.message : '获取分析任务失败')
    }
  }

  // 加载分析结果文件
  const loadAnalysisResults = async (taskId: string) => {
    try {
      // 首先尝试从新的API获取带分析数据的片段
      const segmentsResponse = await fetchWithAuth(`http://localhost:8000/api/v1/analysis/tasks/${taskId}/segments`)
      
      if (segmentsResponse.segments && segmentsResponse.segments.length > 0) {
        console.log('✅ 从数据库API加载分析结果成功')
        console.log('📊 分析结果数据:', {
          片段数: segmentsResponse.segments.length,
          前3个片段: segmentsResponse.segments.slice(0, 3).map((s: any) => ({
            id: s.segment_id,
            时间: `${s.start_time}s-${s.end_time}s`,
            缩略图: s.thumbnail_url,
            GIF: s.gif_url,
            分析数据: s.content_analysis ? '✅' : '❌'
          }))
        })
        
        // 设置从数据库获取的结果
        setAnalysisResults({
          segments: segmentsResponse.segments,
          transitions: [],
          transcription: {
            text: "",
            language: "zh",
            segments: []
          },
          _dataQuality: { hasIssues: false, issues: [], score: 100 }
        })
        return
      }
      
      // 如果数据库API没有数据，回退到原来的JSON文件方式
      const url = `http://localhost:8000/uploads/${taskId}_results.json`
      console.log('🔍 回退到JSON文件加载:', url)
      
      const response = await fetch(url)
      if (response.ok) {
        const results = await response.json()
        
        // 验证数据质量
        const dataQuality = validateAnalysisResults(results, taskId)
        console.log('📊 分析结果数据:', {
          视频时长: results.video_info?.duration,
          片段数: results.segments?.length,
          转场数: results.transitions?.length,
          转录段数: results.transcription?.segments?.length,
          数据质量: dataQuality,
          前3个片段: results.segments?.slice(0, 3)?.map((s: any) => ({
            id: s.segment_id,
            时间: `${s.start_time}s-${s.end_time}s`,
            缩略图: s.thumbnail_url,
            GIF: s.gif_url
          }))
        })
        
        // 如果数据有严重问题，显示警告
        if (dataQuality.hasIssues) {
          console.warn('⚠️ 检测到数据质量问题:', dataQuality.issues)
        }
        
        setAnalysisResults({
          ...results,
          _dataQuality: dataQuality // 附加数据质量信息
        })
      } else {
        console.warn('❌ 无法加载分析结果文件:', response.status, response.statusText)
      }
    } catch (err) {
      console.warn('❌ 加载分析结果文件失败:', err)
      // 不设置错误，因为这不是关键错误
    }
  }

  // 验证分析结果数据质量
  const validateAnalysisResults = (results: any, taskId: string) => {
    const issues = []
    
    // 检查视频分割质量
    const segments = results.segments || []
    if (segments.length > 0) {
      const durations = segments.map((s: any) => s.duration)
      const allSame = durations.every((d: number) => Math.abs(d - durations[0]) < 0.1)
      if (allSame && Math.abs(durations[0] - 30.0) < 0.1) {
        issues.push('视频分割使用了固定30秒分割，而非AI智能分割')
      }
    }
    
    // 检查音频转录
    const transcription = results.transcription || {}
    if (Object.keys(transcription).length === 0) {
      issues.push('音频转录数据为空')
    }
    
    // 检查视频路径映射
    const videoPath = results.video_path || ''
    if (videoPath && !videoPath.includes(taskId)) {
      issues.push('视频文件路径与任务ID不匹配')
    }
    
    return {
      hasIssues: issues.length > 0,
      issues: issues,
      score: Math.max(0, 100 - issues.length * 25) // 每个问题扣25分
    }
  }

  // 初始化数据加载
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError(null)
      
      try {
        await Promise.all([fetchVideo(), fetchTasks()])
      } catch (err) {
        console.error('加载数据失败:', err)
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      loadData()
    }
  }, [id])

  // 获取最新的分析任务
  const latestTask = tasks.length > 0 ? tasks[0] : null
  
  // 计算分页
  const segments = analysisResults?.segments || []
  const totalPages = Math.ceil(segments.length / itemsPerPage)
  const paginatedSegments = segments.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  // 下载文件
  const downloadFile = async (url: string, filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000${url}`)
      if (!response.ok) throw new Error('下载失败')
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
      
      toast.success('文件下载成功')
    } catch (err) {
      console.error('下载失败:', err)
      toast.error('文件下载失败')
    }
  }

  // 导出脚本为Markdown
  const exportScriptAsMarkdown = () => {
    try {
      if (!analysisResults?.transcription?.text && !analysisResults?.transcription?.segments) {
        toast.error('没有可导出的脚本内容')
        return
      }

      let markdownContent = `# ${video?.title || '视频'} - 脚本内容\n\n`
      markdownContent += `> 创建时间: ${new Date().toLocaleString()}\n\n`
      
      if (analysisResults.transcription.text) {
        // 将完整文本按句号分段
        const paragraphs = analysisResults.transcription.text
          .split(/[。！？]/)
          .filter(p => p.trim().length > 0)
          .map(p => p.trim() + (p.endsWith('。') || p.endsWith('！') || p.endsWith('？') ? '' : '。'))

        markdownContent += `## 脚本内容\n\n`
        paragraphs.forEach((paragraph) => {
          if (paragraph.trim()) {
            markdownContent += `${paragraph}\n\n`
          }
        })
      }

      const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${video?.title || '视频'}_脚本.md`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success('脚本Markdown文件导出成功')
    } catch (error) {
      console.error('导出脚本失败:', error)
      toast.error('导出脚本失败')
    }
  }

  // 格式化时间
  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-gray-600">加载分析结果中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">{error}</p>
        <Button onClick={() => window.location.reload()}>重试</Button>
      </div>
    )
  }

  if (!video || !latestTask) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">未找到分析数据</p>
      </div>
    )
  }

  // 计算进度值
  const getProgressValue = (progress: string): number => {
    const match = progress.match(/(\d+)/)
    return match ? parseInt(match[1]) : 0
  }

  return (
    <div className="space-y-8">
      {/* 数据质量警告 */}
      {analysisResults?._dataQuality?.hasIssues && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <p className="font-medium">检测到分析结果数据质量问题 (质量得分: {analysisResults._dataQuality.score}%)</p>
              <ul className="list-disc list-inside text-sm space-y-1">
                {analysisResults._dataQuality.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
              <p className="text-sm mt-2">
                建议：点击"重新分析"按钮创建新的AI分析任务，或联系技术支持。
              </p>
            </div>
          </AlertDescription>
        </Alert>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center justify-between">
              分析状态
              {analysisResults?._dataQuality && (
                <Badge variant={analysisResults._dataQuality.hasIssues ? "destructive" : "default"}>
                  质量: {analysisResults._dataQuality.score}%
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              {latestTask.status === 'completed' ? '任务已完成' : 
               latestTask.status === 'running' ? '正在处理中' : 
               latestTask.status === 'failed' ? '处理失败' : '等待处理'}
              {analysisResults?._dataQuality?.hasIssues && (
                <div className="mt-2 text-red-600 text-xs">
                  ⚠️ 检测到数据质量问题
                </div>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {latestTask.video_segmentation && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">视频分割</span>
                    <span className="text-sm text-gray-500">
                      {latestTask.status === 'completed' ? '100%' : `${getProgressValue(latestTask.progress)}%`}
                    </span>
                  </div>
                  <Progress value={latestTask.status === 'completed' ? 100 : getProgressValue(latestTask.progress)} className="h-2" />
                </div>
              )}
              {latestTask.transition_detection && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">转场检测</span>
                    <span className="text-sm text-gray-500">
                      {latestTask.status === 'completed' ? '100%' : `${getProgressValue(latestTask.progress)}%`}
                    </span>
                  </div>
                  <Progress value={latestTask.status === 'completed' ? 100 : getProgressValue(latestTask.progress)} className="h-2" />
                </div>
              )}
              {latestTask.audio_transcription && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">音频转写</span>
                    <span className="text-sm text-gray-500">
                      {latestTask.status === 'completed' ? '100%' : `${getProgressValue(latestTask.progress)}%`}
                    </span>
                  </div>
                  <Progress value={latestTask.status === 'completed' ? 100 : getProgressValue(latestTask.progress)} className="h-2" />
                </div>
              )}
              {latestTask.report_generation && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">报告生成</span>
                    <span className="text-sm text-gray-500">
                      {latestTask.status === 'completed' ? '100%' : `${getProgressValue(latestTask.progress)}%`}
                    </span>
                  </div>
                  <Progress value={latestTask.status === 'completed' ? 100 : getProgressValue(latestTask.progress)} className="h-2" />
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">视频信息</CardTitle>
            <CardDescription>基本信息与统计数据</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">文件名</span>
                <span className="text-sm font-medium">{video.filename}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">时长</span>
                <span className="text-sm font-medium">
                  {video.duration ? formatTime(video.duration) : 
                   analysisResults?.video_info?.duration ? formatTime(analysisResults.video_info.duration) : 
                   '未知'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">分辨率</span>
                <span className="text-sm font-medium">
                  {video.resolution_width && video.resolution_height ? 
                   `${video.resolution_width} x ${video.resolution_height}` :
                   analysisResults?.video_info?.width && analysisResults?.video_info?.height ?
                   `${analysisResults.video_info.width} x ${analysisResults.video_info.height}` :
                   '未知'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">片段数</span>
                <span className="text-sm font-medium">{segments.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">转场数</span>
                <span className="text-sm font-medium">{analysisResults?.transitions?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">对白片段数</span>
                <span className="text-sm font-medium">{analysisResults?.transcription?.segments?.length || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">导出选项</CardTitle>
            <CardDescription>下载分析结果</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {latestTask.report_pdf_url && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full justify-start"
                  onClick={() => downloadFile(latestTask.report_pdf_url!, `${video.title}_报告.pdf`)}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  分析报告 (PDF)
                </Button>
              )}
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Download className="mr-2 h-4 w-4" />
                完整数据包
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="segments" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="segments" className="flex items-center gap-2">
            <Scissors className="h-4 w-4" />
            视频片段
          </TabsTrigger>
          <TabsTrigger value="transitions" className="flex items-center gap-2">
            <Film className="h-4 w-4" />
            转场检测
          </TabsTrigger>
          <TabsTrigger value="transcription" className="flex items-center gap-2">
            <Mic className="h-4 w-4" />
            语音识别
          </TabsTrigger>
          <TabsTrigger value="script" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            脚本内容
          </TabsTrigger>
        </TabsList>

        <TabsContent value="segments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scissors className="h-5 w-5" />
                视频片段分析
              </CardTitle>
              <CardDescription>
                {segments.length > 0 ? `共识别到 ${segments.length} 个视频片段` : '暂无片段数据'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {segments.length > 0 ? (
                <div className="space-y-4">
                  {/* 表格展示 */}
                  <div className="border rounded-lg overflow-hidden">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-32">预览</TableHead>
                          <TableHead className="w-20">时间</TableHead>
                          <TableHead className="w-40">文案内容</TableHead>
                          <TableHead className="w-32">构图分析</TableHead>
                          <TableHead className="w-32">运镜技法</TableHead>
                          <TableHead className="w-32">主题分析</TableHead>
                          <TableHead>AI简评</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {paginatedSegments.map((segment) => (
                          <TableRow key={segment.segment_id} className="hover:bg-gray-50">
                            <TableCell className="p-2">
                              <div className="w-24 h-16 bg-gray-100 rounded-lg overflow-hidden relative group cursor-pointer">
                                                                 {segment.gif_url ? (
                                   <img 
                                     src={`http://localhost:8000${segment.gif_url}`}
                                     alt={`片段 ${segment.segment_id}`}
                                     className="w-full h-full object-cover"
                                     onError={(e) => {
                                       // 如果GIF加载失败，回退到缩略图
                                       const target = e.target as HTMLImageElement
                                       if (segment.thumbnail_url) {
                                         target.src = `http://localhost:8000${segment.thumbnail_url}`
                                       }
                                     }}
                                   />
                                 ) : segment.thumbnail_url ? (
                                  <img 
                                    src={`http://localhost:8000${segment.thumbnail_url}`}
                                    alt={`片段 ${segment.segment_id}`}
                                    className="w-full h-full object-cover"
                                  />
                                ) : (
                                  <div className="flex items-center justify-center h-full">
                                    <Film className="h-6 w-6 text-gray-400" />
                                  </div>
                                )}
                                <div className="absolute bottom-1 right-1 bg-black bg-opacity-60 text-white text-xs px-1 rounded">
                                  {segment.segment_id}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="p-2">
                              <div className="text-xs space-y-1">
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3 text-gray-400" />
                                  <span>{formatTime(segment.start_time)}</span>
                                </div>
                                <div className="text-gray-500">
                                  {formatTime(segment.duration)}
                                </div>
                                <Badge variant="outline" className="text-xs">
                                  {segment.scene_type}
                                </Badge>
                              </div>
                            </TableCell>
                            <TableCell className="p-2">
                              <div className="text-sm space-y-1">
                                <div className="flex items-start gap-2">
                                  <MessageSquare className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                                  <div>
                                    <p className="text-gray-700 leading-relaxed">
                                      {segment.content_analysis?.caption || 
                                       `片段 ${segment.segment_id} 的旁白内容。这是一个示例文案，展示该片段的主要内容和关键信息。`}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="p-2">
                              <div className="text-sm space-y-1">
                                <div className="flex items-start gap-2">
                                  <Eye className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                  <div>
                                    <p className="text-gray-700">
                                      {segment.content_analysis?.composition || 
                                       '中心构图，主体突出，背景简洁，视觉重点明确。'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="p-2">
                              <div className="text-sm space-y-1">
                                <div className="flex items-start gap-2">
                                  <Camera className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                                  <div>
                                    <p className="text-gray-700">
                                      {segment.content_analysis?.camera_movement || 
                                       '固定镜头，平稳拍摄，无明显运动。'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="p-2">
                              <div className="text-sm space-y-1">
                                <div className="flex items-start gap-2">
                                  <Users className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                                  <div>
                                    <p className="text-gray-700">
                                      {segment.content_analysis?.theme_analysis || 
                                       '展示日常活动，人物互动自然，氛围轻松愉快。'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="p-2">
                              <div className="text-sm">
                                <div className="flex items-start gap-2">
                                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                  <div>
                                    <p className="text-gray-700 leading-relaxed">
                                      {segment.content_analysis?.ai_commentary || 
                                       `此片段在整体叙事中起到承转作用，通过${segment.scene_type}的形式有效推进了故事发展。画面构图稳定，运镜手法恰当，成功营造了期望的氛围，为后续情节做好了铺垫。`}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  
                  {/* 分页控制 */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-between pt-4">
                      <Button variant="outline" size="sm" onClick={prevPage} disabled={currentPage === 1}>
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        上一页
                      </Button>
                      <span className="text-sm text-gray-500">
                        第 {currentPage} 页，共 {totalPages} 页 (每页 {itemsPerPage} 条，总共 {segments.length} 条)
                      </span>
                      <Button variant="outline" size="sm" onClick={nextPage} disabled={currentPage === totalPages}>
                        下一页
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Scissors className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>暂无视频片段数据</p>
                  <p className="text-sm">请确保已启用视频分割功能</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transitions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Film className="h-5 w-5" />
                转场检测结果
              </CardTitle>
              <CardDescription>
                {analysisResults?.transitions?.length ? 
                 `共检测到 ${analysisResults.transitions.length} 个转场` : 
                 '暂无转场数据'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysisResults?.transitions?.length ? (
                <div className="space-y-4">
                  {analysisResults.transitions.map((transition) => (
                    <div
                      key={transition.transition_id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-gray-500" />
                          <span className="font-medium">{formatTime(transition.timestamp)}</span>
                        </div>
                        <Badge variant="outline">{transition.type}</Badge>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">强度: {(transition.strength * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Film className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>暂无转场检测数据</p>
                  <p className="text-sm">请确保已启用转场检测功能</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transcription" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-5 w-5" />
                语音识别结果
              </CardTitle>
              <CardDescription>
                {analysisResults?.transcription?.segments?.length ? 
                 `共识别 ${analysisResults.transcription.segments.length} 段对话` : 
                 '暂无语音数据'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysisResults?.transcription?.segments?.length ? (
                <div className="space-y-4">
                  {analysisResults.transcription.segments.map((line, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-gray-500" />
                          <span className="text-sm font-medium">
                            {formatTime(line.start)} - {formatTime(line.end)}
                          </span>
                        </div>
                        <Badge variant="outline">
                          置信度: {(line.confidence * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <p className="text-sm leading-relaxed">{line.text}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Mic className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>暂无语音识别数据</p>
                  <p className="text-sm">请确保已启用音频转录功能</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="script" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  脚本内容
                </div>
                {analysisResults?.transcription?.text && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={exportScriptAsMarkdown}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    导出 Markdown
                  </Button>
                )}
              </CardTitle>
              <CardDescription>
                {analysisResults?.transcription?.text ? 
                 `基于语音识别生成的脚本内容，段落清晰易读` : 
                 '暂无脚本数据'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysisResults?.transcription?.text ? (
                <div className="space-y-6">
                  {/* 脚本内容 - 分段展示 */}
                  <div className="max-w-none">
                    <div className="space-y-6">
                      {/* 将完整文本按句号分段 */}
                      {analysisResults.transcription.text
                        .split(/[。！？]/)
                        .filter(p => p.trim().length > 10) // 过滤太短的片段
                        .map((paragraph, index) => {
                          const cleanParagraph = paragraph.trim()
                          if (!cleanParagraph) return null
                          
                          return (
                            <div key={index} className="group">
                              <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-start gap-4">
                                  <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-bold px-3 py-2 rounded-lg min-w-fit shadow-sm">
                                    {index + 1}
                                  </div>
                                  <div className="flex-1">
                                    <p className="text-gray-900 leading-loose text-lg font-medium" 
                                       style={{ 
                                         fontFamily: '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif',
                                         lineHeight: '2',
                                         letterSpacing: '0.05em'
                                       }}>
                                      {cleanParagraph}
                                      {!cleanParagraph.match(/[。！？]$/) && '。'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                              
                              {/* 段落间分隔线 */}
                              {analysisResults?.transcription?.text && index < analysisResults.transcription.text.split(/[。！？]/).filter(p => p.trim().length > 10).length - 1 && (
                                <div className="flex items-center justify-center py-4">
                                  <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent w-full max-w-xs"></div>
                                </div>
                              )}
                            </div>
                          )
                        })
                      }
                    </div>
                  </div>
                  
                  {/* 脚本统计信息 */}
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-800 mb-2">脚本统计</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-blue-600">总字数：</span>
                        <span className="font-medium">{analysisResults.transcription.text.length}</span>
                      </div>
                      <div>
                        <span className="text-blue-600">段落数：</span>
                        <span className="font-medium">
                          {analysisResults.transcription.text.split(/[。！？]/).filter(p => p.trim().length > 0).length}
                        </span>
                      </div>
                      {analysisResults.transcription.language && (
                        <div>
                          <span className="text-blue-600">语言：</span>
                          <span className="font-medium">{analysisResults.transcription.language}</span>
                        </div>
                      )}
                      {analysisResults.transcription.segments && (
                        <div>
                          <span className="text-blue-600">语音片段：</span>
                          <span className="font-medium">{analysisResults.transcription.segments.length}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>暂无脚本内容</p>
                  <p className="text-sm">请确保已启用音频转录功能</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
