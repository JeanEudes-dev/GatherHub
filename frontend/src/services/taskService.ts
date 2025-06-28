import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1/`
  : 'http://localhost:8000/api/v1/'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Apply interceptors (similar to authService and eventService)
// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor for handling token refresh (simplified - ideally global)
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      localStorage.getItem('refresh')
    ) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh')
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        })
        const { access, refresh } = response.data
        localStorage.setItem('access', access)
        if (refresh) localStorage.setItem('refresh', refresh)

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + access
        originalRequest.headers['Authorization'] = 'Bearer ' + access
        return apiClient(originalRequest)
      } catch (refreshError) {
        console.error('Token refresh failed in taskService:', refreshError)
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        // Potentially trigger global logout
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

// Task Types (should be in a central types/index.ts)
export interface TaskAssignee {
  id: number
  username: string
  first_name?: string
  last_name?: string
  email?: string
}

export interface TaskCreator {
  id: number
  username: string
}

export interface TaskEventInfo {
  id: number
  title: string
  date?: string // Optional, as per API_REFERENCE.md
}

export interface Task {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high'
  due_date: string | null // ISO 8601 datetime string or null
  event: TaskEventInfo // Can be just event ID on create/update, object on retrieve
  assignee: TaskAssignee | null
  creator: TaskCreator
  created_at: string
  updated_at: string
  completed_at?: string | null
}

export interface EventParticipant {
  id: number
  username: string
  first_name?: string
  last_name?: string
  email?: string
  is_admin: boolean
  is_moderator: boolean
}

export interface PaginatedTasksResponse {
  count: number
  next: string | null
  previous: string | null
  results: Task[]
}

export interface CreateTaskData {
  title: string
  description: string
  event: number // Event ID
  priority?: 'low' | 'medium' | 'high'
  due_date?: string | null // ISO 8601 datetime string
  assignee?: number | null // Assignee User ID
}

export interface UpdateTaskData extends Partial<Omit<CreateTaskData, 'event'>> {
  status?: 'pending' | 'in_progress' | 'completed'
}

export interface AssignTaskData {
  assignee: number // User ID of the assignee
}

// API Functions for Tasks
export const listTasks = async (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params?: Record<string, any>
): Promise<PaginatedTasksResponse> => {
  const response = await apiClient.get('/tasks/', { params })
  return response.data
}

export const createTask = async (taskData: CreateTaskData): Promise<Task> => {
  const response = await apiClient.post('/tasks/', taskData)
  return response.data
}

export const getTaskDetails = async (taskId: number): Promise<Task> => {
  const response = await apiClient.get(`/tasks/${taskId}/`)
  return response.data
}

export const updateTask = async (
  taskId: number,
  taskData: UpdateTaskData
): Promise<Task> => {
  const response = await apiClient.put(`/tasks/${taskId}/`, taskData)
  return response.data
}

// API_REFERENCE.md does not explicitly list DELETE /tasks/{id}/, but it's a common REST practice.
// If it's not supported by the backend, this function will fail.
export const deleteTask = async (taskId: number): Promise<void> => {
  await apiClient.delete(`/tasks/${taskId}/`)
}

export const assignTask = async (
  taskId: number,
  assigneeId: number
): Promise<{ message: string; task: Partial<Task> }> => {
  const response = await apiClient.post(`/tasks/${taskId}/assign/`, {
    assignee: assigneeId,
  })
  return response.data
}

export const completeTask = async (
  taskId: number
): Promise<{ message: string; task: Partial<Task> }> => {
  const response = await apiClient.post(`/tasks/${taskId}/complete/`)
  return response.data
}
