import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8008';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          const authStorage = localStorage.getItem('auth-storage');
          if (authStorage) {
            try {
              const { state } = JSON.parse(authStorage);
              if (state?.token) {
                config.headers.Authorization = `Bearer ${state.token}`;
              }
            } catch (e) {
              console.error('Error parsing auth storage:', e);
            }
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth-storage');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  getInstance() {
    return this.client;
  }
}

export const apiClient = new ApiClient().getInstance();
