import { createClient } from '@supabase/supabase-js';

// 构建时使用占位符值，运行时使用真实值
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder-service-key';

// 环境配置：根据NODE_ENV确定数据库schema
const getEnvironmentConfig = () => {
  const isProduction = process.env.NODE_ENV === 'production';
  const schema = isProduction ? 'production' : 'public'; // 开发环境使用public schema
  
  console.log('🔧 Database Environment Config:', {
    NODE_ENV: process.env.NODE_ENV,
    isProduction,
    schema,
    supabaseUrl: supabaseUrl.replace(/\/.*/, '/***') // 隐藏完整URL
  });
  
  return { schema, isProduction };
};

const { schema } = getEnvironmentConfig();

// 服务器端客户端，使用service role key
export const supabaseServer = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  },
  db: {
    schema: schema
  }
});

// 数据库管理器类，支持环境隔离
export class DatabaseManager {
  private supabase = supabaseServer;
  private schema = schema;

  async getUserByEmail(email: string) {
    const { data, error } = await this.supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      console.error(`❌ Database Error (${this.schema}.users):`, error);
      throw error;
    }
    
    console.log(`✅ Database Query (${this.schema}.users):`, data ? 'Found user' : 'No user found');
    return data;
  }

  async createUser(userData: any) {
    console.log(`📝 Creating user in ${this.schema} schema:`, userData.email);
    
    const { data, error } = await this.supabase
      .from('users')
      .insert(userData)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.schema}.users):`, error);
      throw error;
    }
    
    console.log(`✅ User created in ${this.schema} schema:`, data.id);
    return data;
  }

  async getUserTasks(userId: string) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error(`❌ Database Error (${this.schema}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Tasks retrieved from ${this.schema} schema:`, data?.length || 0);
    return data || [];
  }

  async createTask(taskData: any) {
    console.log(`📝 Creating task in ${this.schema} schema:`, taskData.video_id);
    
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .insert(taskData)
      .select()
      .single();
    
    if (error) {
      console.error(`❌ Database Error (${this.schema}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Task created in ${this.schema} schema:`, data.id);
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
      console.error(`❌ Database Error (${this.schema}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Task updated in ${this.schema} schema:`, taskId);
    return data;
  }

  async getTaskById(taskId: string) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('id', taskId)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      console.error(`❌ Database Error (${this.schema}.analysis_tasks):`, error);
      throw error;
    }
    
    console.log(`✅ Task retrieved from ${this.schema} schema:`, data ? 'Found' : 'Not found');
    return data;
  }
}

export const dbManager = new DatabaseManager(); 