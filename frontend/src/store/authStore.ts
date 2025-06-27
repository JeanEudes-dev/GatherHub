import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { getUserProfile as fetchUserProfile, login as apiLogin, register as apiRegister, logout as apiLogout, updateUserProfile as apiUpdateUserProfile } from '../services/authService';

// Define types based on your backend's user model and API responses
// These should ideally be in a central types/index.ts file
interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  bio?: string;
  avatar?: string; // URL to avatar
  date_joined?: string;
  last_login?: string;
}

interface LoginCredentials {
  username?: string;
  email?: string;
  password?: string;
}

interface RegisterData {
  username?: string;
  email?: string;
  password?: string;
  first_name?: string;
  last_name?: string;
}

interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  bio?: string;
  avatar?: File | string | null;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: () => boolean;
  login: (credentials: LoginCredentials) => Promise<User | null>;
  register: (userData: RegisterData) => Promise<User | null>;
  logout: () => Promise<void>;
  fetchProfile: () => Promise<User | null>;
  updateProfile: (profileData: UpdateProfileData) => Promise<User | null>;
  setTokens: (access: string, refresh?: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      error: null,

      isAuthenticated: () => !!get().accessToken && !!get().user,

      setTokens: (access: string, refresh?: string) => {
        set({ accessToken: access, error: null });
        if (refresh) {
          set({ refreshToken: refresh });
        }
        localStorage.setItem('accessToken', access);
        if (refresh) {
          localStorage.setItem('refreshToken', refresh);
        }
      },

      clearAuth: () => {
        set({ user: null, accessToken: null, refreshToken: null, error: null });
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      },

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiLogin(credentials);
          const newAccessToken = localStorage.getItem('accessToken'); // Fetched by apiLogin's interceptor
          const newRefreshToken = localStorage.getItem('refreshToken');
          if (user && newAccessToken) {
            set({ user, accessToken: newAccessToken, refreshToken: newRefreshToken, isLoading: false });
            return user;
          }
          throw new Error("Login failed to return user or token.");
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.response?.data?.error || error.message || 'Login failed';
          set({ isLoading: false, error: errorMessage, user: null, accessToken: null, refreshToken: null });
          get().clearAuth(); // Ensure all auth state is cleared on login failure
          return null;
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiRegister(userData);
          const newAccessToken = localStorage.getItem('accessToken');
          const newRefreshToken = localStorage.getItem('refreshToken');
          if (user && newAccessToken) {
            set({ user, accessToken: newAccessToken, refreshToken: newRefreshToken, isLoading: false });
            return user;
          }
          throw new Error("Registration failed to return user or token.");
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || error.message || 'Registration failed';
          set({ isLoading: false, error: errorMessage, user: null, accessToken: null, refreshToken: null });
          get().clearAuth();
          return null;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        const currentRefreshToken = get().refreshToken;
        try {
          if (currentRefreshToken) {
             await apiLogout(); // authService.logout handles token removal from localStorage
          }
        } catch (error: any) {
          console.error("Server logout failed:", error.message);
          // Still proceed to clear local state
        } finally {
          get().clearAuth();
          set({ isLoading: false });
        }
      },

      fetchProfile: async () => {
        if (!get().accessToken) return null; // No token, no profile
        set({ isLoading: true, error: null });
        try {
          const user = await fetchUserProfile();
          set({ user, isLoading: false });
          return user;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch profile';
          set({ isLoading: false, error: errorMessage });
          if (error.response?.status === 401) { // Token might be invalid/expired
            get().logout(); // Perform logout to clear invalid token
          }
          return null;
        }
      },

      updateProfile: async (profileData: UpdateProfileData) => {
        if (!get().accessToken) throw new Error("Not authenticated");
        set({ isLoading: true, error: null });
        try {
          const updatedUser = await apiUpdateUserProfile(profileData);
          set({ user: updatedUser, isLoading: false });
          return updatedUser;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to update profile';
          set({ isLoading: false, error: errorMessage });
          return null;
        }
      },
    }),
    {
      name: 'auth-storage', // unique name
      storage: createJSONStorage(() => localStorage), // (optional) by default, 'localStorage' is used
      partialize: (state) => ({
        // Persist only these fields
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
      // On rehydration, try to fetch profile if tokens exist
      onRehydrateStorage: () => (state, error) => {
        if (error) {
          console.error("Failed to rehydrate auth store:", error);
          state?.clearAuth();
        } else if (state?.accessToken && !state.user) {
          // If we have a token but no user, try to fetch the user profile.
          // This needs to be done carefully to avoid loops or race conditions.
          // For simplicity, we can trigger it from an effect in App.tsx or a layout component.
          console.log("Rehydrated with token, consider fetching profile.");
        }
      }
    }
  )
);

// Call this on app initialization if tokens are in localStorage but not in Zustand state yet
// (e.g. after a page refresh)
export const rehydrateAuth = () => {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  const state = useAuthStore.getState();

  if (accessToken && !state.accessToken) {
    state.setTokens(accessToken, refreshToken || undefined);
    // It's generally better to fetch the profile in a component effect after rehydration
    // to ensure React context is available and to handle loading states properly.
    // state.fetchProfile();
  }
};

// Initialize rehydration logic. This is a basic way.
// More sophisticated apps might do this in their main App component or a layout effect.
if (typeof window !== 'undefined') {
    rehydrateAuth();
}
