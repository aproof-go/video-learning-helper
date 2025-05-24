import { createClient } from '@supabase/supabase-js';

// 构建时使用占位符值，运行时使用真实值
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder-service-key';

// 服务器端客户端，使用service role key
export const supabaseServer = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

// 数据库管理器类，移植自FastAPI版本
export class DatabaseManager {
  private supabase = supabaseServer;

  async getUserByEmail(email: string) {
    const { data, error } = await this.supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      throw error;
    }
    
    return data;
  }

  async createUser(userData: any) {
    const { data, error } = await this.supabase
      .from('users')
      .insert(userData)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async getUserTasks(userId: number) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data || [];
  }

  async createTask(taskData: any) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .insert(taskData)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async updateTask(taskId: number, updates: any) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .update(updates)
      .eq('id', taskId)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async getTaskById(taskId: number) {
    const { data, error } = await this.supabase
      .from('analysis_tasks')
      .select('*')
      .eq('id', taskId)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      throw error;
    }
    
    return data;
  }
}

export const dbManager = new DatabaseManager(); 