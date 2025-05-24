"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { videoApi, analysisApi, VideoResponse, AnalysisTaskResponse, ApiError } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Play, 
  Download, 
  Trash2, 
  Clock, 
  FileVideo, 
  AlertCircle,
  Upload,
  Eye,
  RefreshCw
} from "lucide-react"

// 使用VideoResponse，因为它现在已经包含了可选的tasks字段
type VideoWithTasks = VideoResponse & { tasks: AnalysisTaskResponse[] }

export default function VideosPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [videos, setVideos] = useState<VideoWithTasks[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  
  const PAGE_SIZE = 12 // 每页12个视频
  const MAX_RETRIES = 3

  useEffect(() => {
    if (user) {
      loadVideos()
    }
  }, [user])

  const loadVideos = async (isLoadMore = false) => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error("请先登录")
      }

      if (isLoadMore) {
        setLoadingMore(true)
      } else {
        setLoading(true)
        setError(null)
        setPage(0)
        setHasMore(true)
      }

      const currentPage = isLoadMore ? page + 1 : 0
      const skip = currentPage * PAGE_SIZE

      // 使用带任务信息的API，避免N+1查询问题
      const videosData = await videoApi.getUserVideos(token, skip, PAGE_SIZE, true)
      
      // 确保每个视频都有tasks数组
      const videosWithTasks = videosData.map(video => ({
        ...video,
        tasks: video.tasks || []
      }))
      
      if (isLoadMore) {
        setVideos(prev => [...prev, ...videosWithTasks])
        setPage(currentPage)
      } else {
        setVideos(videosWithTasks)
        setPage(0)
      }
      
      // 如果返回的数据少于每页数量，说明没有更多数据了
      setHasMore(videosData.length === PAGE_SIZE)
      
    } catch (err) {
      console.error('Failed to load videos:', err)
      if (err instanceof ApiError && err.status === 401) {
        setError("登录已过期，请重新登录")
      } else {
        setError(`加载视频列表失败${retryCount > 0 ? ` (重试 ${retryCount}/${MAX_RETRIES})` : ''}`)
      }
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  const loadMoreVideos = () => {
    if (!loadingMore && hasMore) {
      loadVideos(true)
    }
  }

  const retryLoadVideos = () => {
    if (retryCount < MAX_RETRIES) {
      setRetryCount(prev => prev + 1)
      loadVideos()
    }
  }

  const resetAndReload = () => {
    setRetryCount(0)
    setError(null)
    loadVideos()
  }

  const [deletingVideoId, setDeletingVideoId] = useState<string | null>(null)

  const handleDeleteVideo = async (videoId: string) => {
    if (!confirm("确定要删除这个视频吗？此操作不可恢复。")) {
      return
    }

    setDeletingVideoId(videoId)
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error("请先登录")
      }

      await videoApi.deleteVideo(videoId, token)
      setVideos(videos.filter(v => v.id !== videoId))
    } catch (err) {
      console.error('Failed to delete video:', err)
      alert("删除失败，请稍后重试")
    } finally {
      setDeletingVideoId(null)
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
          <p className="text-gray-500 mb-6">您需要登录后才能查看视频列表</p>
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">我的视频</h1>
          <p className="text-gray-500 mt-2">管理您上传的视频和分析结果</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => loadVideos()} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            刷新
          </Button>
          <Button onClick={() => router.push('/#upload')}>
            <Upload className="h-4 w-4 mr-2" />
            上传视频
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <div className="flex gap-2">
              {retryCount < MAX_RETRIES && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={retryLoadVideos}
                  disabled={loading}
                >
                  重试 ({MAX_RETRIES - retryCount})
                </Button>
              )}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={resetAndReload}
                disabled={loading}
              >
                刷新
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {videos.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <FileVideo className="h-16 w-16 text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">还没有视频</h2>
          <p className="text-gray-500 mb-6">上传您的第一个视频开始分析</p>
          <Button onClick={() => router.push('/#upload')}>
            <Upload className="h-4 w-4 mr-2" />
            上传视频
          </Button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map((video) => (
              <Card key={video.id} className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg truncate">{video.title}</CardTitle>
                      <CardDescription className="mt-1">
                        {video.filename}
                      </CardDescription>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteVideo(video.id)}
                      disabled={deletingVideoId === video.id}
                      className="text-red-500 hover:text-red-700 disabled:opacity-50"
                    >
                      {deletingVideoId === video.id ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-500"></div>
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* 视频信息 */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">大小:</span>
                      <span className="ml-1">{formatFileSize(video.file_size)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">时长:</span>
                      <span className="ml-1">{formatDuration(video.duration)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">格式:</span>
                      <span className="ml-1 uppercase">{video.format || '未知'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">分辨率:</span>
                      <span className="ml-1">
                        {video.resolution_width && video.resolution_height 
                          ? `${video.resolution_width}x${video.resolution_height}`
                          : '未知'
                        }
                      </span>
                    </div>
                  </div>

                  {/* 分析任务状态 */}
                  <div>
                    <h4 className="text-sm font-medium mb-2">分析任务</h4>
                    {video.tasks.length === 0 ? (
                      <p className="text-sm text-gray-500">暂无分析任务</p>
                    ) : (
                      <div className="space-y-2">
                        {video.tasks.map((task) => (
                          <div key={task.id} className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <Clock className="h-3 w-3 text-gray-400" />
                              <span className="text-sm">
                                {new Date(task.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            {getStatusBadge(task.status)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/analysis/${video.id}`)}
                      className="flex-1"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      查看
                    </Button>
                    {video.file_url && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(video.file_url, '_blank')}
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* 加载更多按钮 */}
          {hasMore && (
            <div className="flex justify-center">
              <Button 
                variant="outline" 
                onClick={loadMoreVideos}
                disabled={loadingMore}
                className="min-w-[120px]"
              >
                {loadingMore ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                    加载中...
                  </>
                ) : (
                  '加载更多'
                )}
              </Button>
            </div>
          )}
          
          {/* 显示总数信息 */}
          <div className="text-center text-sm text-gray-500">
            已显示 {videos.length} 个视频
            {!hasMore && videos.length > 0 && ' • 已显示全部'}
          </div>
        </div>
      )}
    </div>
  )
} 