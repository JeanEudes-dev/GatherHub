/**
 * Application constants and configuration
 */

// API Configuration
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

// App Information
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'GatherHub'
export const APP_VERSION = '1.0.0'

// Theme Configuration
export const THEME = {
  aurora: {
    blue: '#00D4FF',
    purple: '#B84FFF',
    pink: '#FF4FD1',
    green: '#4FFF88',
    yellow: '#FFD700',
  },
  glass: {
    light: 'rgba(255, 255, 255, 0.05)',
    medium: 'rgba(255, 255, 255, 0.1)',
    heavy: 'rgba(255, 255, 255, 0.15)',
  },
} as const

// Animation Durations
export const ANIMATION = {
  fast: 150,
  normal: 300,
  slow: 500,
} as const

// Breakpoints (matching Tailwind)
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
  user: 'gatherhub_user',
  theme: 'gatherhub_theme',
  preferences: 'gatherhub_preferences',
  token: 'gatherhub_token',
} as const

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const

// Event Types
export const EVENT_TYPES = {
  MEETING: 'meeting',
  WORKSHOP: 'workshop',
  CONFERENCE: 'conference',
  SOCIAL: 'social',
  OTHER: 'other',
} as const

// Task Status
export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
} as const

// Vote Types
export const VOTE_TYPES = {
  YES_NO: 'yes_no',
  MULTIPLE_CHOICE: 'multiple_choice',
  RATING: 'rating',
  RANKING: 'ranking',
} as const

// WebSocket Events
export const WS_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  JOIN_ROOM: 'join_room',
  LEAVE_ROOM: 'leave_room',
  MESSAGE: 'message',
  NOTIFICATION: 'notification',
  UPDATE: 'update',
} as const

// File Upload
export const FILE_UPLOAD = {
  maxSize: 10 * 1024 * 1024, // 10MB
  allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
} as const

// Pagination
export const PAGINATION = {
  defaultPageSize: 20,
  maxPageSize: 100,
} as const

// Form Validation
export const VALIDATION = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  password: {
    minLength: 8,
    maxLength: 128,
  },
  username: {
    minLength: 3,
    maxLength: 30,
    pattern: /^[a-zA-Z0-9_]+$/,
  },
} as const
