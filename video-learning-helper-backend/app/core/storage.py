"""
文件存储服务
支持本地存储、Supabase Storage 和 AWS S3
"""

import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
from urllib.parse import urljoin

from app.core.config import get_settings

settings = get_settings()

class StorageService(ABC):
    """存储服务基类"""
    
    @abstractmethod
    async def upload_file(
        self, 
        file: BinaryIO, 
        filename: str, 
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        上传文件
        Returns: (file_id, file_url)
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """获取文件URL"""
        pass

class LocalStorageService(StorageService):
    """本地文件存储服务"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_file(
        self, 
        file: BinaryIO, 
        filename: str, 
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """上传文件到本地目录"""
        # 生成唯一文件名
        file_ext = Path(filename).suffix
        file_id = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / file_id
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = file.read()
            buffer.write(content)
        
        # 返回文件ID和URL
        file_url = f"/uploads/{file_id}"
        return file_id, file_url
    
    async def delete_file(self, file_id: str) -> bool:
        """删除本地文件"""
        try:
            file_path = self.upload_dir / file_id
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"删除本地文件失败: {e}")
            return False
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """获取本地文件URL"""
        file_path = self.upload_dir / file_id
        if file_path.exists():
            return f"/uploads/{file_id}"
        return None

class SupabaseStorageService(StorageService):
    """Supabase Storage 存储服务"""
    
    def __init__(self):
        try:
            from supabase import create_client
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            self.bucket_name = settings.storage_bucket
            print(f"✅ Supabase Storage 初始化成功，桶名: {self.bucket_name}")
        except ImportError:
            raise ImportError("请安装 supabase 依赖: pip install supabase")
        except Exception as e:
            print(f"❌ Supabase Storage 初始化失败: {e}")
            raise
    
    async def upload_file(
        self, 
        file: BinaryIO, 
        filename: str, 
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """上传文件到 Supabase Storage"""
        try:
            # 生成唯一文件名
            file_ext = Path(filename).suffix
            file_id = f"{uuid.uuid4()}{file_ext}"
            
            # 读取文件内容
            file_content = file.read()
            
            # 上传到 Supabase Storage
            result = self.client.storage.from_(self.bucket_name).upload(
                path=file_id,
                file=file_content,
                file_options={
                    "content-type": content_type or "application/octet-stream"
                }
            )
            
            if result.status_code != 200:
                raise Exception(f"Supabase Storage 上传失败: {result}")
            
            # 获取公共URL
            file_url = self.client.storage.from_(self.bucket_name).get_public_url(file_id)
            
            print(f"✅ 文件上传到 Supabase Storage 成功: {file_id}")
            return file_id, file_url
            
        except Exception as e:
            print(f"❌ Supabase Storage 上传失败: {e}")
            raise
    
    async def delete_file(self, file_id: str) -> bool:
        """从 Supabase Storage 删除文件"""
        try:
            result = self.client.storage.from_(self.bucket_name).remove([file_id])
            if result.status_code == 200:
                print(f"✅ 从 Supabase Storage 删除文件成功: {file_id}")
                return True
            else:
                print(f"❌ 从 Supabase Storage 删除文件失败: {result}")
                return False
        except Exception as e:
            print(f"❌ Supabase Storage 删除失败: {e}")
            return False
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """获取 Supabase Storage 文件的公共URL"""
        try:
            file_url = self.client.storage.from_(self.bucket_name).get_public_url(file_id)
            return file_url
        except Exception as e:
            print(f"❌ 获取 Supabase Storage 文件URL失败: {e}")
            return None

class AWSS3StorageService(StorageService):
    """AWS S3 存储服务"""
    
    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.bucket_name = settings.storage_bucket
            print(f"✅ AWS S3 初始化成功，桶名: {self.bucket_name}")
        except ImportError:
            raise ImportError("请安装 boto3 依赖: pip install boto3")
        except Exception as e:
            print(f"❌ AWS S3 初始化失败: {e}")
            raise
    
    async def upload_file(
        self, 
        file: BinaryIO, 
        filename: str, 
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """上传文件到 AWS S3"""
        try:
            # 生成唯一文件名
            file_ext = Path(filename).suffix
            file_id = f"{uuid.uuid4()}{file_ext}"
            
            # 上传到 S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_id,
                ExtraArgs={
                    'ContentType': content_type or 'application/octet-stream'
                }
            )
            
            # 生成公共URL
            file_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_id}"
            
            print(f"✅ 文件上传到 AWS S3 成功: {file_id}")
            return file_id, file_url
            
        except Exception as e:
            print(f"❌ AWS S3 上传失败: {e}")
            raise
    
    async def delete_file(self, file_id: str) -> bool:
        """从 AWS S3 删除文件"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_id)
            print(f"✅ 从 AWS S3 删除文件成功: {file_id}")
            return True
        except Exception as e:
            print(f"❌ AWS S3 删除失败: {e}")
            return False
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """获取 AWS S3 文件的公共URL"""
        try:
            file_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_id}"
            return file_url
        except Exception as e:
            print(f"❌ 获取 AWS S3 文件URL失败: {e}")
            return None

def get_storage_service() -> StorageService:
    """根据配置获取存储服务实例"""
    if settings.use_local_storage or settings.storage_provider == "local":
        return LocalStorageService()
    elif settings.storage_provider == "supabase":
        return SupabaseStorageService()
    elif settings.storage_provider == "aws_s3":
        return AWSS3StorageService()
    else:
        print(f"⚠️ 不支持的存储提供商: {settings.storage_provider}，使用本地存储")
        return LocalStorageService()

# 全局存储服务实例
storage_service = get_storage_service() 