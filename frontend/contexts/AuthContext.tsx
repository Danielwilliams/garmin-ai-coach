'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { AuthContextType, User, AuthTokens, LoginRequest, RegisterRequest } from '@/types/auth';
import { authAPI, TokenManager } from '@/lib/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      // Check if we have stored tokens
      const storedTokens = TokenManager.getTokens();
      if (!storedTokens) {
        setIsLoading(false);
        return;
      }

      setTokens(storedTokens);

      // Try to get current user with stored tokens
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Auth initialization failed:', error);
      // Clear invalid tokens
      TokenManager.clearTokens();
      setTokens(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      setIsLoading(true);
      
      // Login and get tokens
      const authTokens = await authAPI.login(credentials);
      setTokens(authTokens);

      // Get user info
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      // Clear any stored tokens on failed login
      TokenManager.clearTokens();
      setTokens(null);
      setUser(null);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest): Promise<void> => {
    try {
      setIsLoading(true);
      
      // Register user (doesn't return tokens)
      await authAPI.register(data);

      // Automatically login after successful registration
      await login({
        email: data.email,
        password: data.password
      });
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    authAPI.logout();
    setUser(null);
    setTokens(null);
  };

  const refreshTokens = async (): Promise<void> => {
    try {
      const newTokens = await authAPI.refreshTokens();
      setTokens(newTokens);
    } catch (error) {
      // If refresh fails, clear everything and logout
      setUser(null);
      setTokens(null);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    tokens,
    isLoading,
    isAuthenticated: !!user && !!tokens,
    login,
    register,
    logout,
    refreshTokens
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;