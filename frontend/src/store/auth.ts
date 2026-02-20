import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  company_name: string;
  subscription_tier: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  fetchUser: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  company_name: string;
  full_name?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8008';

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const formData = new URLSearchParams();
          formData.append('username', email);
          formData.append('password', password);
          
          const response = await fetch(`${API_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login fehlgeschlagen');
          }

          const data = await response.json();
          
          set({
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          // Fetch user data
          await get().fetchUser();
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login fehlgeschlagen',
            isAuthenticated: false,
            token: null,
            user: null,
          });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(`${API_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registrierung fehlgeschlagen');
          }

          const result = await response.json();
          
          // Auto-login after registration
          await get().login(data.email, data.password);
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Registrierung fehlgeschlagen',
          });
          throw error;
        }
      },

      fetchUser: async () => {
        const token = get().token;
        if (!token) return;

        try {
          const response = await fetch(`${API_URL}/api/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Fehler beim Laden der Benutzerdaten');
          }

          const user = await response.json();
          set({ user, isAuthenticated: true });
        } catch (error) {
          console.error('Error fetching user:', error);
          get().logout();
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
);
