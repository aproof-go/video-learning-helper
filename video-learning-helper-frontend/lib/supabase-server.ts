import { createClient } from '@supabase/supabase-js';

// 环境检测函数
const getEnvironment = (): 'development' | 'production' => {
  // 1. 检查 Vercel 环境变量
  if (process.env.VERCEL_ENV === 'production') return 'production';
  
  // 2. 检查 NODE_ENV
  if (process.env.NODE_ENV === 'production') return 'production';
  
  // 3. 默认为测试环境（包括本地开发）
  return 'development';
};

// 根据环境获取 Supabase 配置
const getSupabaseConfig = () => {
  const environment = getEnvironment();
  
  console.log('🔧 Environment Detection:', {
    NODE_ENV: process.env.NODE_ENV,
    VERCEL_ENV: process.env.VERCEL_ENV,
    DETECTED_ENV: environment
  });
  
  switch (environment) {
    case 'development':
      // 测试环境：使用现有配置
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL_DEV || process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co',
        serviceKey: process.env.SUPABASE_SERVICE_ROLE_KEY_DEV || process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder-service-key'
      };
    
    case 'production':
      // 生产环境：独立的 ap-production 项目
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL_PROD || process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co',
        serviceKey: process.env.SUPABASE_SERVICE_ROLE_KEY_PROD || process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder-service-key'
      };
    
    default:
      return {
        url: process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co',
        serviceKey: process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder-service-key'
      };
  }
};

const supabaseConfig = getSupabaseConfig();
const environment = getEnvironment();

console.log('🔧 Supabase Server Config:', {
  environment,
  url: supabaseConfig.url,
  hasServiceKey: !!supabaseConfig.serviceKey && supabaseConfig.serviceKey !== 'placeholder-service-key'
});

// 服务器端客户端，使用service role key
export const supabaseServer = createClient(supabaseConfig.url, supabaseConfig.serviceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

// 数据库管理器类
export class DatabaseManager {
  private supabase = supabaseServer;
  private environment = environment;

  async getUserByEmail(email: string) {
    console.log(`🔍 Getting user by email in ${this.environment} environment`);
    
    const { data, error } = await this.supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      console.error(`❌ Database Error (${this.environment}.users):`, error);
      throw error;
    }
    
    console.log(`✅ Database Query (${this.environment}.users):`, data ? 'Found user' : 'No user found');
    return data;
  }

  async createUser(userData: any) {
    console.log(`📝 Creating user in ${this.environment} environment:`, userData.email);
    
    const { data, error } = await this.supabase
      .from('users')
      .insert(userData)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.users):`, error);
      throw error;
    }
    
    console.log(`✅ User created in ${this.environment} environment:`, data.id);
    return data;
  }

  async getUserTasks(userId: string) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Tasks retrieved from ${this.environment} environment:`, data?.length || 0);
    return data || [];
  }

  async createTask(taskData: any) {
    console.log(`📝 Creating task in ${this.environment} environment:`, taskData.video_id);
    
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .insert(taskData)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Task created in ${this.environment} environment:`, data.id);
    return data;
  }

  async updateTask(taskId: string, updates: any) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .update(updates)
      .eq('id', taskId)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Task updated in ${this.environment} environment:`, taskId);
    return data;
  }

  async getTaskById(taskId: string) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('id', taskId)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      console.error(`❌ Database Error (${this.environment}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Task retrieved from ${this.environment} environment:`, data ? 'Found' : 'Not found');
    return data;
  }

  // 视频相关方法
  async createVideo(videoData: any) {
    console.log(`📝 Creating video in ${this.environment} environment:`, videoData.title);
    
    const { data, error } = await this.supabase
      .from('videos')
      .insert(videoData)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.videos):`, error);
      throw error;
    }
    
    console.log(`✅ Video created in ${this.environment} environment:`, data.id);
    return data;
  }

  async getUserVideos(userId: string, skip: number = 0, limit: number = 100) {
    console.log(`🔍 Getting user videos in ${this.environment} environment for user: ${userId}`);
    
    const { data, error } = await this.supabase
      .from('videos')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .range(skip, skip + limit - 1);
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.videos):`, error);
      throw error;
    }
    
    console.log(`✅ Videos retrieved from ${this.environment} environment:`, data?.length || 0);
    return data || [];
  }

  async getVideoById(videoId: string) {
    console.log(`🔍 Getting video by ID in ${this.environment} environment: ${videoId}`);
    
    const { data, error } = await this.supabase
      .from('videos')
      .select('*')
      .eq('id', videoId)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      console.error(`❌ Database Error (${this.environment}.videos):`, error);
      throw error;
    }
    
    console.log(`✅ Video retrieved from ${this.environment} environment:`, data ? 'Found' : 'Not found');
    return data;
  }

  async getVideoAnalysisTasks(videoId: string) {
    console.log(`🔍 Getting video analysis tasks in ${this.environment} environment for video: ${videoId}`);
    
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('video_id', videoId)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Video analysis tasks retrieved from ${this.environment} environment:`, data?.length || 0);
    return data || [];
  }

  async updateVideo(videoId: string, updates: any) {
    console.log(`📝 Updating video in ${this.environment} environment: ${videoId}`);
    
    const { data, error } = await this.supabase
      .from('videos')
      .update(updates)
      .eq('id', videoId)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.videos):`, error);
      throw error;
    }
    
    console.log(`✅ Video updated in ${this.environment} environment:`, videoId);
    return data;
  }

  async deleteVideo(videoId: string) {
    console.log(`🗑️ Deleting video in ${this.environment} environment: ${videoId}`);
    
    const { data, error } = await this.supabase
      .from('videos')
      .delete()
      .eq('id', videoId)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.environment}.videos):`, error);
      throw error;
    }
    
    console.log(`✅ Video deleted from ${this.environment} environment:`, videoId);
    return data;
  }
}

export const dbManager = new DatabaseManager(); 