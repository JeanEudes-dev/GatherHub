import React, { useEffect, useState } from 'react'
import { useTaskStore } from '../../store/taskStore'
import type { Task, EventParticipant } from '../../services/taskService' // Assuming Task type is exported
import TaskItem from './TaskItem'
import TaskForm from './TaskForm'
import { Button } from '../../components/ui/button'
import { PlusCircle } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { motion } from 'framer-motion'

interface TaskListProps {
  eventId: number
  eventParticipants: EventParticipant[]
  isEventCreator: boolean // Passed from EventDetailPage
}

const TaskList: React.FC<TaskListProps> = ({
  eventId,
  eventParticipants,
  isEventCreator,
}) => {
  const { tasks, fetchTasksByEvent, isLoading, error } = useTaskStore()
  const { isAuthenticated, user: currentUser } = useAuthStore()
  const [isTaskFormOpen, setIsTaskFormOpen] = useState(false)
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null)

  useEffect(() => {
    if (eventId) {
      fetchTasksByEvent(eventId)
    }
  }, [eventId, fetchTasksByEvent])

  const handleOpenNewTaskForm = () => {
    setTaskToEdit(null)
    setIsTaskFormOpen(true)
  }

  const handleEditTask = (task: Task) => {
    setTaskToEdit(task)
    setIsTaskFormOpen(true)
  }

  const handleCloseTaskForm = () => {
    setIsTaskFormOpen(false)
    setTaskToEdit(null) // Clear taskToEdit when form closes
    // Optionally, refetch tasks for the event to ensure UI consistency,
    // though individual actions in TaskStore should ideally update the state.
    // fetchTasksByEvent(eventId);
  }

  // Filter tasks into categories
  const pendingTasks = tasks.filter(
    task => task.event.id === eventId && task.status === 'pending'
  )
  const inProgressTasks = tasks.filter(
    task => task.event.id === eventId && task.status === 'in_progress'
  )
  const completedTasks = tasks.filter(
    task => task.event.id === eventId && task.status === 'completed'
  )

  const canCreateTask =
    typeof isAuthenticated === 'function'
      ? isAuthenticated() &&
        (isEventCreator || eventParticipants.some(p => p.id === currentUser?.id))
      : isAuthenticated &&
        (isEventCreator || eventParticipants.some(p => p.id === currentUser?.id))

  if (isLoading && tasks.length === 0) {
    return (
      <div className="py-6 text-center text-gray-400">Loading tasks...</div>
    )
  }

  if (error) {
    return (
      <div className="py-6 text-center text-red-400">
        Error loading tasks: {error}
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-semibold text-white">Tasks</h3>
        {canCreateTask && (
          <Button onClick={handleOpenNewTaskForm} className="btn-glass text-sm">
            <PlusCircle size={18} className="mr-2" /> Add Task
          </Button>
        )}
      </div>

      {tasks.filter(task => task.event.id === eventId).length === 0 &&
        !isLoading && (
          <div className="glass-card rounded-md p-6 text-center">
            <p className="text-gray-400">
              No tasks have been added for this event yet.
            </p>
            {canCreateTask && (
              <Button
                onClick={handleOpenNewTaskForm}
                variant="link"
                className="mt-2 text-aurora-blue"
              >
                Add the first task
              </Button>
            )}
          </div>
        )}

      {/* Pending Tasks */}
      {pendingTasks.length > 0 && (
        <div>
          <h4 className="mb-3 text-lg font-medium text-gray-300">
            Pending ({pendingTasks.length})
          </h4>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {pendingTasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <TaskItem
                  task={task}
                  eventParticipants={eventParticipants}
                  onEdit={handleEditTask}
                  isEventCreator={isEventCreator}
                />
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* In Progress Tasks */}
      {inProgressTasks.length > 0 && (
        <div>
          <h4 className="mb-3 text-lg font-medium text-yellow-400">
            In Progress ({inProgressTasks.length})
          </h4>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {inProgressTasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <TaskItem
                  task={task}
                  eventParticipants={eventParticipants}
                  onEdit={handleEditTask}
                  isEventCreator={isEventCreator}
                />
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div>
          <h4 className="mb-3 text-lg font-medium text-green-400">
            Completed ({completedTasks.length})
          </h4>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {completedTasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <TaskItem
                  task={task}
                  eventParticipants={eventParticipants}
                  onEdit={handleEditTask}
                  isEventCreator={isEventCreator}
                />
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {isTaskFormOpen && (
        <TaskForm
          isOpen={isTaskFormOpen}
          onClose={handleCloseTaskForm}
          eventParticipants={eventParticipants}
          eventId={eventId}
          taskToEdit={taskToEdit}
        />
      )}
    </div>
  )
}

export default TaskList
