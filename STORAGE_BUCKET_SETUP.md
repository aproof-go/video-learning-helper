# 📦 Supabase 存储桶权限配置指南

## 🎯 目标
解决 `row-level security policy` 错误，允许用户上传文件到存储桶。

## 🔧 配置步骤

### 1. 访问存储桶设置
```
1. 打开 https://supabase.com/dashboard/project/iinqgyutxdmswssjoqvt
2. 进入 Storage → 选择存储桶 "video-learning-prod"
3. 点击右上角的 "Policies" 标签
```

### 2. 创建上传策略

#### 策略1：允许公开上传（简单方案）
```sql
-- 策略名称：Allow public uploads
-- 操作：INSERT
-- 目标角色：public
-- Using 表达式：
true

-- With check 表达式：
true
```

#### 策略2：允许认证用户上传（安全方案）
```sql
-- 策略名称：Allow authenticated uploads
-- 操作：INSERT  
-- 目标角色：authenticated
-- Using 表达式：
auth.role() = 'authenticated'

-- With check 表达式：
auth.role() = 'authenticated'
```

#### 策略3：用户只能上传到自己的文件夹（最安全）
```sql
-- 策略名称：Users can upload to own folder
-- 操作：INSERT
-- 目标角色：authenticated
-- Using 表达式：
(auth.uid())::text = (storage.foldername(name))[2]

-- With check 表达式：
(auth.uid())::text = (storage.foldername(name))[2]
```

### 3. 创建下载策略

#### 允许公开下载
```sql
-- 策略名称：Allow public downloads
-- 操作：SELECT
-- 目标角色：public
-- Using 表达式：
true
```

### 4. 验证配置
```
1. 刷新存储桶页面
2. 确认策略已生效
3. 测试文件上传功能
```

## 🚨 推荐配置

对于生产环境，推荐使用：
- **上传**：策略1（Allow public uploads）- 简单有效
- **下载**：Allow public downloads - 允许访问上传的文件

## 🔍 故障排除

如果仍有问题：
1. 检查存储桶是否设为 Public
2. 确认 RLS 策略已保存
3. 检查控制台是否有其他错误信息 