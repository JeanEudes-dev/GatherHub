import axios from 'axios'; // Assuming axios is already installed and configured in a similar way to authService

// Re-establish apiClient if not globally available or create a new one.
// For simplicity, I'll redefine it here. In a larger app, this would be centralized.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Simplified response interceptor for this service.
// Token refresh logic should ideally be handled globally by the main apiClient instance.
// If authService.ts's apiClient is globally configured, this might not be needed here.
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry && localStorage.getItem('refreshToken')) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, { refresh: refreshToken });
        const { access, refresh } = response.data;
        localStorage.setItem('accessToken', access);
        if (refresh) localStorage.setItem('refreshToken', refresh);

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + access; // For global axios if used
        originalRequest.headers['Authorization'] = 'Bearer ' + access;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error("Token refresh failed in eventService:", refreshError);
        // Potentially trigger logout action from authStore
        // const { logout } = useAuthStore.getState(); logout();
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login'; // Force redirect
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Types for Event data (should ideally be in a central types/index.ts)
// Based on API_REFERENCE.md
export interface EventCreator {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
}

export interface EventParticipant {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
}

export interface Event {
  id: number;
  title: string;
  description: string;
  date: string; // ISO 8601 datetime string
  location: string;
  max_participants: number;
  current_participants: number;
  status: 'upcoming' | 'ongoing' | 'completed'; // Or as defined by backend
  creator: EventCreator;
  participants?: EventParticipant[]; // Optional, might be in detailed view
  tasks?: any[]; // Placeholder, replace with Task type
  votes?: any[]; // Placeholder, replace with Vote type
  created_at: string;
  updated_at: string;
}

export interface PaginatedEventsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Event[];
}

export interface CreateEventData {
  title: string;
  description: string;
  date: string; // ISO 8601 datetime string
  location: string;
  max_participants: number;
}

export interface UpdateEventData extends Partial<CreateEventData> {}

// API Functions
export const listEvents = async (params?: Record<string, any>): Promise<PaginatedEventsResponse> => {
  const response = await apiClient.get('/events/', { params });
  return response.data;
};

export const createEvent = async (eventData: CreateEventData): Promise<Event> => {
  const response = await apiClient.post('/events/', eventData);
  return response.data;
};

export const getEventDetails = async (eventId: number): Promise<Event> => {
  const response = await apiClient.get(`/events/${eventId}/`);
  return response.data;
};

export const updateEvent = async (eventId: number, eventData: UpdateEventData): Promise<Event> => {
  const response = await apiClient.put(`/events/${eventId}/`, eventData);
  return response.data;
};

export const deleteEvent = async (eventId: number): Promise<void> => {
  await apiClient.delete(`/events/${eventId}/`);
};

export const joinEvent = async (eventId: number): Promise<{ message: string; event: { id: number; title: string; current_participants: number } }> => {
  const response = await apiClient.post(`/events/${eventId}/join/`);
  return response.data;
};

export const leaveEvent = async (eventId: number): Promise<{ message: string; event: { id: number; title: string; current_participants: number } }> => {
  const response = await apiClient.post(`/events/${eventId}/leave/`);
  return response.data;
};
