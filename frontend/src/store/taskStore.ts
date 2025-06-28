/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from 'zustand'
import {
  listTasks as apiListTasks,
  createTask as apiCreateTask,
  getTaskDetails as apiGetTaskDetails,
  updateTask as apiUpdateTask,
  deleteTask as apiDeleteTask,
  assignTask as apiAssignTask,
  completeTask as apiCompleteTask,
  type Task,
  type CreateTaskData,
  type UpdateTaskData,
  type PaginatedTasksResponse,
} from '../services/taskService'

interface TaskState {
  tasks: Task[] // Typically tasks associated with a specific event, or all tasks if global view
  currentTask: Task | null
  isLoading: boolean
  error: string | null
  pagination: {
    // If listing tasks globally with pagination
    count: number
    next: string | null
    previous: string | null
    currentPage: number
    pageSize: number
  }

  // Actions
  fetchTasksByEvent: (
    eventId: number,
    params?: Record<string, any>
  ) => Promise<void> // Most common use case
  fetchTaskById: (taskId: number) => Promise<Task | null>
  createTask: (
    taskData: CreateTaskData,
    eventId: number
  ) => Promise<Task | null> // eventId to update specific event's tasks
  updateTask: (
    taskId: number,
    taskData: UpdateTaskData,
    eventId?: number
  ) => Promise<Task | null>
  deleteTask: (taskId: number, eventId?: number) => Promise<boolean>
  assignTask: (
    taskId: number,
    assigneeId: number,
    eventId?: number
  ) => Promise<boolean>
  completeTask: (taskId: number, eventId?: number) => Promise<boolean>

  // Real-time updates (placeholders)
  handleTaskCreated: (task: Task) => void
  handleTaskUpdated: (task: Task) => void
  handleTaskDeleted: (taskId: number, eventId?: number) => void
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  currentTask: null,
  isLoading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 10, // Default for global task lists, may not be used if always event-specific
  },

  // Primarily fetch tasks for a specific event
  fetchTasksByEvent: async (eventId: number, params?: Record<string, any>) => {
    set({ isLoading: true, error: null })
    try {
      // Assuming listTasks can filter by event ID
      const response: PaginatedTasksResponse = await apiListTasks({
        ...params,
        event: eventId,
      })
      set({
        tasks: response.results, // These are tasks for the specific event
        isLoading: false,
        // Pagination here would be for tasks within that event, if backend supports it
        pagination: {
          ...get().pagination,
          count: response.count,
          next: response.next,
          previous: response.previous,
          currentPage: params?.page || 1,
        },
      })
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || error.message || 'Failed to fetch tasks'
      set({ isLoading: false, error: errorMessage, tasks: [] })
    }
  },

  fetchTaskById: async (taskId: number) => {
    set({ isLoading: true, error: null })
    try {
      const task = await apiGetTaskDetails(taskId)
      set({ currentTask: task, isLoading: false })
      // Update in list if present
      set(state => ({
        tasks: state.tasks.map(t => (t.id === taskId ? task : t)),
      }))
      return task
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Failed to fetch task details'
      set({ isLoading: false, error: errorMessage, currentTask: null })
      return null
    }
  },

  createTask: async (taskData: CreateTaskData, eventId: number) => {
    set({ isLoading: true, error: null })
    try {
      const newTask = await apiCreateTask(taskData)
      // Add to tasks list if the current list is for this event
      if (taskData.event === eventId) {
        // Ensure it's the correct event context
        set(state => ({ tasks: [newTask, ...state.tasks] })) // Or refetch
      }
      // A full refetch might be simpler if dealing with complex sorting/pagination
      // await get().fetchTasksByEvent(eventId);
      set({ isLoading: false })
      return newTask
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || error.message || 'Failed to create task'
      set({ isLoading: false, error: errorMessage })
      return null
    }
  },

  updateTask: async (taskId: number, taskData: UpdateTaskData) => {
    set({ isLoading: true, error: null })
    try {
      const updatedTask = await apiUpdateTask(taskId, taskData)
      set(state => ({
        tasks: state.tasks.map(task =>
          task.id === taskId ? updatedTask : task
        ),
        currentTask:
          state.currentTask?.id === taskId ? updatedTask : state.currentTask,
        isLoading: false,
      }))
      return updatedTask
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || error.message || 'Failed to update task'
      set({ isLoading: false, error: errorMessage })
      return null
    }
  },

  deleteTask: async (taskId: number) => {
    set({ isLoading: true, error: null })
    try {
      await apiDeleteTask(taskId)
      set(state => ({
        tasks: state.tasks.filter(task => task.id !== taskId),
        currentTask:
          state.currentTask?.id === taskId ? null : state.currentTask,
        isLoading: false,
      }))
      // If eventId provided and tasks list becomes empty, could refetch or handle pagination
      return true
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || error.message || 'Failed to delete task'
      set({ isLoading: false, error: errorMessage })
      return false
    }
  },

  assignTask: async (taskId: number, assigneeId: number) => {
    set({ isLoading: true, error: null })
    try {
      await apiAssignTask(taskId, assigneeId)
      // Refetch task or update optimistically
      const updatedTaskDetails = await apiGetTaskDetails(taskId)
      set(state => ({
        tasks: state.tasks.map(task =>
          task.id === taskId ? updatedTaskDetails : task
        ),
        currentTask:
          state.currentTask?.id === taskId
            ? updatedTaskDetails
            : state.currentTask,
        isLoading: false,
      }))
      return true
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || error.message || 'Failed to assign task'
      set({ isLoading: false, error: errorMessage })
      return false
    }
  },

  completeTask: async (taskId: number) => {
    set({ isLoading: true, error: null })
    try {
      await apiCompleteTask(taskId)
      const updatedTaskDetails = await apiGetTaskDetails(taskId) // Refetch to get completed_at and accurate status
      set(state => ({
        tasks: state.tasks.map(task =>
          task.id === taskId ? updatedTaskDetails : task
        ),
        currentTask:
          state.currentTask?.id === taskId
            ? updatedTaskDetails
            : state.currentTask,
        isLoading: false,
      }))
      return true
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Failed to complete task'
      set({ isLoading: false, error: errorMessage })
      return false
    }
  },

  // WebSocket Handlers
  handleTaskCreated: (newTask: Task) => {
    // Check if the task's event matches a context or if it should be added globally
    // This logic depends on how tasks are displayed (e.g., are they always within an event view?)
    set(state => {
      // Avoid duplicates if also received via normal API call
      if (!state.tasks.find(t => t.id === newTask.id)) {
        // Add to list if relevant (e.g. if currentEvent.id === newTask.event.id)
        // For simplicity, if tasks are for a specific event, check currentEvent
        const currentEventId = useEventStore.getState().currentEvent?.id
        if (currentEventId && newTask.event.id === currentEventId) {
          return { tasks: [newTask, ...state.tasks] }
        }
      }
      return {} // No change if not relevant or duplicate
    })
  },

  handleTaskUpdated: (updatedTask: Task) => {
    set(state => ({
      tasks: state.tasks.map(task =>
        task.id === updatedTask.id ? updatedTask : task
      ),
      currentTask:
        state.currentTask?.id === updatedTask.id
          ? updatedTask
          : state.currentTask,
    }))
  },

  handleTaskDeleted: (taskId: number) => {
    set(state => ({
      tasks: state.tasks.filter(task => task.id !== taskId),
      currentTask: state.currentTask?.id === taskId ? null : state.currentTask,
    }))
  },
}))

// Import useEventStore to access currentEvent for context in WebSocket handlers
import { useEventStore } from './eventStore'
