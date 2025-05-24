'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { authApi, tokenManager, UserResponse } from '@/lib/api'

interface AuthContextType {
  user: UserResponse | null
  isLoading: boolean
  login: (token: string) => Promise<void>
  logout: () => void
  updateUser: (user: UserResponse) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // 检查本地存储的token并获取用户信息
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = tokenManager.getToken()
        if (token) {
          const userData = await authApi.getCurrentUser(token)
          setUser(userData)
        }
      } catch (error) {
        // Token可能过期或无效，清除本地存储
        tokenManager.removeToken()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (token: string) => {
    try {
      setIsLoading(true)
      tokenManager.saveToken(token)
      const userData = await authApi.getCurrentUser(token)
      setUser(userData)
    } catch (error) {
      tokenManager.removeToken()
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    tokenManager.removeToken()
    setUser(null)
  }

  const updateUser = (userData: UserResponse) => {
    setUser(userData)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 