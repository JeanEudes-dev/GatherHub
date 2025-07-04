/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react'
import type { Task } from '../../services/taskService'
import { useTaskStore } from '../../store/taskStore'
import { useAuthStore } from '../../store/authStore'
import { Button } from '../../components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../../components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../../components/ui/avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select'
// import { toast } from 'sonner';
import type { EventParticipant } from '../../services/eventService' // For assignee selection
import { Edit3, Trash2, UserPlus, CheckCircle, Circle } from 'lucide-react' // Icons
import toast from 'react-hot-toast'

interface TaskItemProps {
  task: Task
  eventParticipants: EventParticipant[] // To populate assignee dropdown
  onEdit: (task: Task) => void // Callback to open edit form
  isEventCreator: boolean // To determine if delete/assign actions are allowed
}

// Helper for date formatting
const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateString
  }
}

const TaskItem: React.FC<TaskItemProps> = ({
  task,
  eventParticipants,
  onEdit,
  isEventCreator,
}) => {
  const {
    completeTask,
    assignTask,
    deleteTask,
    isLoading: isTaskStoreLoading,
  } = useTaskStore()
  const { user: currentUser } = useAuthStore()
  const [isAssigning, setIsAssigning] = useState(false)
  const [selectedAssignee, setSelectedAssignee] = useState<string | undefined>(
    task.assignee?.id.toString()
  )

  const canManageTask =
    isEventCreator ||
    currentUser?.id === task.creator.id ||
    currentUser?.id === task.assignee?.id
  const canAssignOrDelete =
    isEventCreator || currentUser?.id === task.creator.id

  const handleCompleteToggle = async () => {
    if (task.status === 'completed') {
      toast('Task is already completed. To un-complete, edit the task status.')
      return
    }
    const success = await completeTask(task.id, task.event.id)
    if (success) toast.success(`Task "${task.title}" marked as complete!`)
    else toast.error('Failed to update task status.')
  }

  const handleAssigneeChange = async (assigneeId: string) => {
    setSelectedAssignee(assigneeId)
    if (assigneeId) {
      const success = await assignTask(
        task.id,
        parseInt(assigneeId),
        task.event.id
      )
      if (success) toast.success(`Task assigned successfully.`)
      else toast.error('Failed to assign task.')
    }
    setIsAssigning(false)
  }

  const handleDelete = async () => {
    const confirmed = window.confirm(
      `Are you sure you want to delete task: "${task.title}"?`
    )
    if (confirmed) {
      const success = await deleteTask(task.id, task.event.id)
      if (success) toast.success('Task deleted.')
      else toast.error('Failed to delete task.')
    }
  }

  const priorityColor = {
    low: 'bg-blue-500/20 text-blue-300',
    medium: 'bg-yellow-500/20 text-yellow-300',
    high: 'bg-red-500/20 text-red-300',
  }

  const statusIcon = {
    pending: <Circle size={18} className="mr-2 text-gray-400" />,
    in_progress: (
      <Circle size={18} className="mr-2 animate-pulse text-yellow-400" />
    ), // Simple pulse for in_progress
    completed: <CheckCircle size={18} className="mr-2 text-green-400" />,
  }

  return (
    <Card
      className={`glass-card hover:shadow-aurora overflow-hidden transition-all duration-300 ${task.status === 'completed' ? 'opacity-70' : ''}`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle
            className={`text-lg font-semibold ${task.status === 'completed' ? 'text-gray-400 line-through' : 'text-white'}`}
          >
            {task.title}
          </CardTitle>
          <div
            className={`rounded-full px-2 py-0.5 text-xs ${priorityColor[task.priority]}`}
          >
            {task.priority}
          </div>
        </div>
        <CardDescription className="text-xs text-gray-400">
          Due: {formatDate(task.due_date)}
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-4 text-sm text-gray-300">
        <p className="mb-3 min-h-[40px]">{task.description}</p>

        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center">
            {statusIcon[task.status]}
            <span className="text-xs capitalize">
              {task.status.replace('_', ' ')}
            </span>
          </div>
          {task.assignee ? (
            <div className="flex items-center gap-2 text-xs">
              <Avatar className="h-6 w-6 text-xs">
                <AvatarImage
                  src={(task.assignee as any).avatar}
                  alt={task.assignee.username}
                />
                <AvatarFallback>
                  {task.assignee.first_name
                    ? task.assignee.first_name.charAt(0)
                    : task.assignee.username.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <span>{task.assignee.first_name || task.assignee.username}</span>
            </div>
          ) : (
            <span className="text-xs italic text-gray-500">Unassigned</span>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between bg-white/5 p-3">
        <div className="flex items-center gap-2">
          {(currentUser?.id === task.assignee?.id || canManageTask) &&
            task.status !== 'completed' && (
              <Button
                size="icon"
                variant="ghost"
                onClick={handleCompleteToggle}
                className="h-8 w-8 text-green-400 hover:text-green-300"
                title="Mark as complete"
                disabled={isTaskStoreLoading}
              >
                <CheckCircle size={16} />
              </Button>
            )}
          {task.status === 'completed' && (
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 cursor-default text-green-400"
              title="Completed"
              disabled
            >
              <CheckCircle size={16} />
            </Button>
          )}

          {isAssigning && canAssignOrDelete ? (
            <Select
              onValueChange={handleAssigneeChange}
              defaultValue={selectedAssignee}
            >
              <SelectTrigger className="h-8 w-[150px] border-gray-600 bg-gray-700 text-xs text-white">
                <SelectValue placeholder="Assign to..." />
              </SelectTrigger>
              <SelectContent className="border-gray-700 bg-gray-800 text-white">
                <SelectItem value="" className="text-xs italic">
                  Unassign
                </SelectItem>
                {eventParticipants.map(p => (
                  <SelectItem
                    key={p.id}
                    value={p.id.toString()}
                    className="text-xs"
                  >
                    {p.first_name || p.username}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            canAssignOrDelete && (
              <Button
                size="icon"
                variant="ghost"
                onClick={() => setIsAssigning(true)}
                className="h-8 w-8 text-blue-400 hover:text-blue-300"
                title="Assign task"
                disabled={isTaskStoreLoading}
              >
                <UserPlus size={16} />
              </Button>
            )
          )}
        </div>

        <div className="flex items-center gap-1">
          {canManageTask && (
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onEdit(task)}
              className="h-8 w-8 text-yellow-400 hover:text-yellow-300"
              title="Edit task"
              disabled={isTaskStoreLoading}
            >
              <Edit3 size={16} />
            </Button>
          )}
          {canAssignOrDelete && (
            <Button
              size="icon"
              variant="ghost"
              onClick={handleDelete}
              className="h-8 w-8 text-red-400 hover:text-red-300"
              title="Delete task"
              disabled={isTaskStoreLoading}
            >
              <Trash2 size={16} />
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}

export default TaskItem
