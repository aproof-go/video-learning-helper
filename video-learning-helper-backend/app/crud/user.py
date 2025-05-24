from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserCRUD:
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查邮箱是否已存在
        existing_user = await self.get_by_email(db, user_create.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # 创建新用户
        db_user = User(
            email=user_create.email,
            name=user_create.name,
        )
        
        db.add(db_user)
        try:
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Email already registered")
    
    async def update(self, db: AsyncSession, user: User, user_update: UserUpdate) -> User:
        """更新用户信息"""
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def authenticate(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = await self.get_by_email(db, email)
        if not user:
            return None
        
        # 注意：由于使用Supabase Auth，这里暂时跳过密码验证
        # 实际应用中应该通过Supabase Auth API进行验证
        return user


# 创建CRUD实例
user_crud = UserCRUD() 