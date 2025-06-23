/**
 * Global TypeScript type definitions for GatherHub
 */

// User Types
export interface User {
  id: string
  username: string
  email: string
  firstName: string
  lastName: string
  avatar?: string
  isActive: boolean
  dateJoined: string
  lastLogin?: string
}

export interface UserProfile extends User {
  bio?: string
  location?: string
  website?: string
  socialLinks?: {
    twitter?: string
    linkedin?: string
    github?: string
  }
}

// Authentication Types
export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  firstName: string
  lastName: string
}

// Event Types
export interface Event {
  id: string
  title: string
  description: string
  eventType: 'meeting' | 'workshop' | 'conference' | 'social' | 'other'
  startDate: string
  endDate: string
  location?: string
  isVirtual: boolean
  maxParticipants?: number
  currentParticipants: number
  organizer: User
  participants: User[]
  status: 'draft' | 'published' | 'ongoing' | 'completed' | 'cancelled'
  createdAt: string
  updatedAt: string
}

export interface CreateEventData {
  title: string
  description: string
  eventType: Event['eventType']
  startDate: string
  endDate: string
  location?: string
  isVirtual: boolean
  maxParticipants?: number
}

// Task Types
export interface Task {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignedTo?: User
  assignedBy: User
  event?: Event
  dueDate?: string
  completedAt?: string
  createdAt: string
  updatedAt: string
}

export interface CreateTaskData {
  title: string
  description: string
  priority: Task['priority']
  assignedTo?: string
  eventId?: string
  dueDate?: string
}

// Voting Types
export interface Vote {
  id: string
  title: string
  description: string
  voteType: 'yes_no' | 'multiple_choice' | 'rating' | 'ranking'
  options: VoteOption[]
  allowMultiple: boolean
  isAnonymous: boolean
  startDate: string
  endDate: string
  createdBy: User
  event?: Event
  status: 'draft' | 'active' | 'closed'
  createdAt: string
  updatedAt: string
}

export interface VoteOption {
  id: string
  text: string
  voteCount: number
}

export interface UserVote {
  id: string
  vote: Vote
  option: VoteOption
  user: User
  createdAt: string
}

export interface CreateVoteData {
  title: string
  description: string
  voteType: Vote['voteType']
  options: string[]
  allowMultiple: boolean
  isAnonymous: boolean
  startDate: string
  endDate: string
  eventId?: string
}

// API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count: number
  next?: string
  previous?: string
  results: T[]
}

// WebSocket Types
export interface WebSocketMessage {
  type: string
  data: unknown
  timestamp: string
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  isRead: boolean
  createdAt: string
  user: string
}

// UI State Types
export interface LoadingState {
  isLoading: boolean
  error?: string
}

export interface FormState<T> {
  data: T
  errors: Record<keyof T, string>
  isSubmitting: boolean
  isValid: boolean
}

// Component Props Types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'default' | 'glass' | 'aurora' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  disabled?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

export interface InputProps extends BaseComponentProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  placeholder?: string
  value?: string
  defaultValue?: string
  onChange?: (value: string) => void
  onBlur?: () => void
  onFocus?: () => void
  disabled?: boolean
  required?: boolean
  error?: string
}

// Theme Types
export interface Theme {
  aurora: {
    blue: string
    purple: string
    pink: string
    green: string
    yellow: string
  }
  glass: {
    light: string
    medium: string
    heavy: string
  }
}

// Store Types (for Zustand)
export interface AuthStore {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  register: (data: RegisterData) => Promise<void>
  refreshToken: () => Promise<void>
}

export interface EventStore {
  events: Event[]
  currentEvent: Event | null
  isLoading: boolean
  error: string | null
  fetchEvents: () => Promise<void>
  fetchEvent: (id: string) => Promise<void>
  createEvent: (data: CreateEventData) => Promise<Event>
  updateEvent: (id: string, data: Partial<CreateEventData>) => Promise<Event>
  deleteEvent: (id: string) => Promise<void>
  joinEvent: (id: string) => Promise<void>
  leaveEvent: (id: string) => Promise<void>
}

export interface TaskStore {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  fetchTasks: () => Promise<void>
  createTask: (data: CreateTaskData) => Promise<Task>
  updateTask: (id: string, data: Partial<CreateTaskData>) => Promise<Task>
  deleteTask: (id: string) => Promise<void>
  markTaskComplete: (id: string) => Promise<void>
}

export interface VoteStore {
  votes: Vote[]
  userVotes: UserVote[]
  isLoading: boolean
  error: string | null
  fetchVotes: () => Promise<void>
  createVote: (data: CreateVoteData) => Promise<Vote>
  castVote: (voteId: string, optionId: string) => Promise<void>
  fetchUserVotes: () => Promise<void>
}

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type Nullable<T> = T | null

export type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never
