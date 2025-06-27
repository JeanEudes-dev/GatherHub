import React, { useState, useEffect } from 'react';
import { Task, CreateTaskData, UpdateTaskData, EventParticipant } from '../../services/taskService';
import { useTaskStore } from '../../store/taskStore';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogClose } from '../../components/ui/dialog';
// import { toast } from 'sonner';

interface TaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  eventParticipants: EventParticipant[];
  eventId: number;
  taskToEdit?: Task | null; // If provided, form is in edit mode
}

const TaskForm: React.FC<TaskFormProps> = ({ isOpen, onClose, eventParticipants, eventId, taskToEdit }) => {
  const { createTask, updateTask, isLoading, error } = useTaskStore();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState(''); // YYYY-MM-DD
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [assigneeId, setAssigneeId] = useState<string | undefined>(undefined);
  const [status, setStatus] = useState<'pending' | 'in_progress' | 'completed'>('pending');
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (taskToEdit) {
      setTitle(taskToEdit.title);
      setDescription(taskToEdit.description);
      setDueDate(taskToEdit.due_date ? taskToEdit.due_date.split('T')[0] : ''); // Assumes ISO string
      setPriority(taskToEdit.priority);
      setAssigneeId(taskToEdit.assignee?.id.toString());
      setStatus(taskToEdit.status);
    } else {
      // Reset for new task form
      setTitle('');
      setDescription('');
      setDueDate('');
      setPriority('medium');
      setAssigneeId(undefined);
      setStatus('pending');
    }
    setFormError(null); // Clear errors when form opens or taskToEdit changes
  }, [taskToEdit, isOpen]); // Rerun when isOpen changes to reset form if taskToEdit is null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!title) {
      setFormError('Title is required.');
      return;
    }

    const taskData = {
      title,
      description,
      priority,
      due_date: dueDate || null, // Send null if empty
      assignee: assigneeId ? Number(assigneeId) : null,
    };

    let success = false;
    if (taskToEdit) {
      const updateData: UpdateTaskData = { ...taskData, status };
      const updated = await updateTask(taskToEdit.id, updateData, eventId);
      if (updated) success = true;
    } else {
      const createData: CreateTaskData = { ...taskData, event: eventId };
      const created = await createTask(createData, eventId);
      if (created) success = true;
    }

    if (success) {
      // toast.success(taskToEdit ? 'Task updated successfully!' : 'Task created successfully!');
      onClose(); // Close dialog on success
    } else {
      setFormError(error || `Failed to ${taskToEdit ? 'update' : 'create'} task.`);
      // toast.error(error || `Failed to ${taskToEdit ? 'update' : 'create'} task.`);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[525px] glass-card text-white border-gray-700">
        <DialogHeader>
          <DialogTitle className="text-2xl text-white">{taskToEdit ? 'Edit Task' : 'Create New Task'}</DialogTitle>
          <DialogDescription className="text-gray-400">
            {taskToEdit ? 'Update the details for this task.' : 'Fill in the details for the new task.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div>
            <Label htmlFor="title" className="text-gray-300">Title</Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-500"/>
          </div>
          <div>
            <Label htmlFor="description" className="text-gray-300">Description</Label>
            <Textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} className="bg-white/10 border-white/20 placeholder-gray-500"/>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="dueDate" className="text-gray-300">Due Date</Label>
              <Input id="dueDate" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="bg-white/10 border-white/20"/>
            </div>
            <div>
              <Label htmlFor="priority" className="text-gray-300">Priority</Label>
              <Select value={priority} onValueChange={(v) => setPriority(v as any)}>
                <SelectTrigger className="bg-white/10 border-white/20">
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 text-white">
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label htmlFor="assigneeId" className="text-gray-300">Assign To</Label>
            <Select value={assigneeId} onValueChange={(v) => setAssigneeId(v === "" ? undefined : v)}>
              <SelectTrigger className="bg-white/10 border-white/20">
                <SelectValue placeholder="Select assignee (optional)" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700 text-white">
                <SelectItem value=""><em>Unassigned</em></SelectItem>
                {eventParticipants.map(p => (
                  <SelectItem key={p.id} value={p.id.toString()}>{p.first_name || p.username}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {taskToEdit && (
            <div>
              <Label htmlFor="status" className="text-gray-300">Status</Label>
              <Select value={status} onValueChange={(v) => setStatus(v as any)}>
                <SelectTrigger className="bg-white/10 border-white/20">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 text-white">
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
          {formError && <p className="text-sm text-red-400 text-center">{formError}</p>}
          <DialogFooter className="pt-4">
            <DialogClose asChild>
                <Button type="button" variant="outline" className="btn-glass">Cancel</Button>
            </DialogClose>
            <Button type="submit" className="btn-aurora" disabled={isLoading}>
              {isLoading ? 'Saving...' : (taskToEdit ? 'Save Changes' : 'Create Task')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default TaskForm;
