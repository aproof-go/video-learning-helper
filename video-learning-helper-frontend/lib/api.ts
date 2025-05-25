// API配置 - 支持测试、生产环境分离
const getEnvironment = (): 'development' | 'production' => {
  // 1. 检查 Vercel 环境变量
  if (process.env.VERCEL_ENV === 'production') return 'production';
  
  // 2. 检查 NODE_ENV
  if (process.env.NODE_ENV === 'production') return 'production';
  
  // 3. 默认为测试环境（包括本地开发）
  return 'development';
};

const getApiBaseUrl = () => {
  const environment = getEnvironment();
  
  // 1. 优先使用直接的环境变量配置
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // 2. 根据环境选择对应的API URL
  switch (environment) {
    case 'development':
      // 测试环境：本地开发或测试部署
      return process.env.NEXT_PUBLIC_DEV_API_URL || 'http://localhost:8000';
    
    case 'production':
      // 生产环境：使用当前域名
      if (typeof window !== 'undefined') {
        return window.location.origin;
      }
      return '';
    
    default:
      return 'http://localhost:8000';
  }
};

const getSupabaseConfig = () => {
  const environment = getEnvironment();
  
  switch (environment) {
    case 'development':
      // 测试环境：使用现有配置
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL_DEV || process.env.NEXT_PUBLIC_SUPABASE_URL,
        anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY_DEV || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
      };
    
    case 'production':
      // 生产环境：独立的 ap-production 项目
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL_PROD || process.env.NEXT_PUBLIC_SUPABASE_URL,
        anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY_PROD || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
      };
    
    default:
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL,
        anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
      };
  }
};

const API_BASE_URL = getApiBaseUrl();
const SUPABASE_CONFIG = getSupabaseConfig();
const ENVIRONMENT = getEnvironment();

export const BACKEND_BASE_URL = API_BASE_URL;

console.log('🔧 API Configuration:', {
  ENVIRONMENT,
  NODE_ENV: process.env.NODE_ENV,
  VERCEL_ENV: process.env.VERCEL_ENV,
  API_BASE_URL,
  SUPABASE_URL: SUPABASE_CONFIG.url,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_DEV_API_URL: process.env.NEXT_PUBLIC_DEV_API_URL
});

// API请求类型
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  name?: string
  created_at: string
}

// 视频相关类型
export interface VideoResponse {
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
  tasks?: AnalysisTaskResponse[]
}

export interface AnalysisTaskResponse {
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

export interface AnalysisTaskCreate {
  video_id: string
  video_segmentation?: boolean
  transition_detection?: boolean
  audio_transcription?: boolean
  report_generation?: boolean
}

export interface UploadResponse {
  message: string
  video_id: string
  upload_url?: string
}

// API错误类型
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

// 通用API请求函数
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  }
  
  console.log(`🌐 apiRequest (${ENVIRONMENT}): URL:`, url)
  console.log('⚙️ apiRequest: Final config:', config)
  console.log('📋 apiRequest: Headers:', config.headers)
  console.log('📦 apiRequest: Body:', config.body)

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (Array.isArray(errorData.detail)) {
          // Pydantic 验证错误格式
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.')} : ${err.msg}`
          ).join(', ')
        } else {
          errorMessage = JSON.stringify(errorData.detail)
        }
      }
      
      throw new ApiError(response.status, errorMessage)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError(0, '网络连接失败，请检查您的网络连接')
  }
}

// 文件上传专用请求函数
async function uploadRequest<T>(
  endpoint: string,
  formData: FormData,
  token: string,
  onProgress?: (progress: number) => void
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && onProgress) {
        const progress = (event.loaded / event.total) * 100
        onProgress(progress)
      }
    })
    
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText)
          resolve(response)
        } catch (error) {
          reject(new ApiError(xhr.status, '响应解析失败'))
        }
      } else {
        try {
          const errorData = JSON.parse(xhr.responseText)
          let errorMessage = `HTTP ${xhr.status}: ${xhr.statusText}`
          
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail
            } else if (Array.isArray(errorData.detail)) {
              // Pydantic 验证错误格式
              errorMessage = errorData.detail.map((err: any) => 
                `${err.loc?.join('.')} : ${err.msg}`
              ).join(', ')
            } else {
              errorMessage = JSON.stringify(errorData.detail)
            }
          }
          
          reject(new ApiError(xhr.status, errorMessage))
        } catch {
          reject(new ApiError(xhr.status, `HTTP ${xhr.status}: ${xhr.statusText}`))
        }
      }
    })
    
    xhr.addEventListener('error', () => {
      reject(new ApiError(0, '网络连接失败'))
    })
    
    xhr.open('POST', url)
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.send(formData)
  })
}

// 认证API
export const authApi = {
  // 用户注册
  register: async (data: RegisterRequest): Promise<UserResponse> => {
    return apiRequest<UserResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 用户登录
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 获取当前用户信息
  getCurrentUser: async (token: string): Promise<UserResponse> => {
    return apiRequest<UserResponse>('/api/users/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}

// 视频API
export const videoApi = {
  // 上传视频
  upload: async (
    file: File,
    title: string,
    description: string,
    token: string,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('description', description)
    
    return uploadRequest<UploadResponse>('/api/videos/upload', formData, token, onProgress)
  },

  // 获取用户视频列表
  getUserVideos: async (token: string, skip = 0, limit = 100, includeTasks = false): Promise<VideoResponse[]> => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      include_tasks: includeTasks.toString()
    })
    return apiRequest<VideoResponse[]>(`/api/v1/videos?${params}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  // 获取视频详情
  getVideo: async (videoId: string, token: string): Promise<VideoResponse> => {
    return apiRequest<VideoResponse>(`/api/v1/videos/${videoId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  // 删除视频
  deleteVideo: async (videoId: string, token: string): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>(`/api/v1/videos/${videoId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}

// 分析任务API
export const analysisApi = {
  // 创建分析任务
  createTask: async (data: AnalysisTaskCreate, token: string): Promise<AnalysisTaskResponse> => {
    console.log('🚀 API: Creating analysis task with data:', data)
    console.log('🎯 API: JSON.stringify result:', JSON.stringify(data))
    
    const requestConfig = {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }
    
    console.log('📤 API: Request config:', requestConfig)
    
    return apiRequest<AnalysisTaskResponse>('/api/v1/analysis/tasks', requestConfig)
  },

  // 获取用户分析任务列表
  getUserTasks: async (token: string, skip = 0, limit = 100): Promise<AnalysisTaskResponse[]> => {
    return apiRequest<AnalysisTaskResponse[]>(`/api/v1/analysis/tasks?skip=${skip}&limit=${limit}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  // 获取分析任务详情
  getTask: async (taskId: string, token: string): Promise<AnalysisTaskResponse> => {
    return apiRequest<AnalysisTaskResponse>(`/api/v1/analysis/tasks/${taskId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  // 获取视频的分析任务
  getVideoTasks: async (videoId: string, token: string): Promise<AnalysisTaskResponse[]> => {
    return apiRequest<AnalysisTaskResponse[]>(`/api/v1/analysis/videos/${videoId}/tasks`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}

// 系统API
export const systemApi = {
  // 健康检查
  health: async () => {
    return apiRequest<{
      status: string
      version: string
      database: string
      user_count: number
    }>('/api/health')
  },
}

// Token管理
export const tokenManager = {
  // 保存token到localStorage
  saveToken: (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  },

  // 从localStorage获取token
  getToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token')
    }
    return null
  },

  // 删除token
  removeToken: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  },
} 