import axios, { AxiosInstance, AxiosResponse } from 'axios';
import Cookies from 'js-cookie';
import { AuthTokens, LoginRequest, RegisterRequest, User, ApiError } from '@/types/auth';

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
class TokenManager {
  private static ACCESS_TOKEN_KEY = 'access_token';
  private static REFRESH_TOKEN_KEY = 'refresh_token';

  static getAccessToken(): string | null {
    return Cookies.get(TokenManager.ACCESS_TOKEN_KEY) || null;
  }

  static getRefreshToken(): string | null {
    return Cookies.get(TokenManager.REFRESH_TOKEN_KEY) || null;
  }

  static setTokens(tokens: AuthTokens): void {
    // Set access token with shorter expiry (30 minutes)
    Cookies.set(TokenManager.ACCESS_TOKEN_KEY, tokens.access_token, {
      expires: 1/48, // 30 minutes
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    });

    // Set refresh token with longer expiry (7 days)
    Cookies.set(TokenManager.REFRESH_TOKEN_KEY, tokens.refresh_token, {
      expires: 7,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    });
  }

  static clearTokens(): void {
    Cookies.remove(TokenManager.ACCESS_TOKEN_KEY);
    Cookies.remove(TokenManager.REFRESH_TOKEN_KEY);
  }

  static getTokens(): AuthTokens | null {
    const accessToken = TokenManager.getAccessToken();
    const refreshToken = TokenManager.getRefreshToken();

    if (!accessToken || !refreshToken) {
      return null;
    }

    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer'
    };
  }
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If unauthorized and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenManager.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Attempt to refresh tokens
        const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken
        });

        const newTokens: AuthTokens = response.data;
        TokenManager.setTokens(newTokens);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
        return api(originalRequest);

      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        TokenManager.clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  async login(credentials: LoginRequest): Promise<AuthTokens> {
    try {
      const response: AxiosResponse<AuthTokens> = await api.post('/auth/login', credentials);
      TokenManager.setTokens(response.data);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Login failed',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async register(data: RegisterRequest): Promise<User> {
    try {
      const response: AxiosResponse<User> = await api.post('/auth/register', data);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Registration failed',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response: AxiosResponse<User> = await api.get('/auth/me');
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to get user info',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async refreshTokens(): Promise<AuthTokens> {
    try {
      const refreshToken = TokenManager.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response: AxiosResponse<AuthTokens> = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      TokenManager.setTokens(response.data);
      return response.data;
    } catch (error: any) {
      TokenManager.clearTokens();
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Token refresh failed',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  logout(): void {
    TokenManager.clearTokens();
  }
};

// Analysis API functions
export const analysisAPI = {
  async getAnalyses(): Promise<any[]> {
    try {
      const response = await api.get('/analyses');
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to fetch analyses',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async getAnalysis(analysisId: string): Promise<any> {
    try {
      const response = await api.get(`/analyses/${analysisId}`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to fetch analysis',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async createAnalysis(data: any): Promise<any> {
    try {
      const response = await api.post('/analyses', data);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to create analysis',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async getAnalysisResults(analysisId: string): Promise<any[]> {
    try {
      const response = await api.get(`/analyses/${analysisId}/results`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to fetch analysis results',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async generateReport(analysisId: string): Promise<any> {
    try {
      const response = await api.post(`/analyses/${analysisId}/generate-report`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to generate report',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async exportData(analysisId: string, format: string = 'json'): Promise<any> {
    try {
      const response = await api.post(`/analyses/${analysisId}/export-data?export_format=${format}`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to export data',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async exportWeeklyPlan(analysisId: string): Promise<any> {
    try {
      const response = await api.post(`/analyses/${analysisId}/export-weekly-plan`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to export weekly plan',
        status: error.response?.status
      };
      throw apiError;
    }
  }
};

// Training Profile API functions
export const trainingProfileAPI = {
  async getProfiles(): Promise<any[]> {
    try {
      const response = await api.get('/training-profiles/');
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to fetch training profiles',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async getProfile(profileId: string): Promise<any> {
    try {
      const response = await api.get(`/training-profiles/${profileId}`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to fetch training profile',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async createProfile(data: any): Promise<any> {
    try {
      const response = await api.post('/training-profiles/from-wizard', data);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to create training profile',
        status: error.response?.status
      };
      throw apiError;
    }
  },

  async startAnalysis(profileId: string): Promise<any> {
    try {
      const response = await api.post(`/training-profiles/${profileId}/start-analysis`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || 'Failed to start AI analysis',
        status: error.response?.status
      };
      throw apiError;
    }
  }
};

export { TokenManager };
export default api;