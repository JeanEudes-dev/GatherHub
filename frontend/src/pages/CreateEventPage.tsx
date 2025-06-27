import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEventStore } from '../store/eventStore';
import { CreateEventData } from '../services/eventService';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea'; // Assuming shadcn/ui textarea
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
// import { toast } from 'sonner';

const CreateEventPage: React.FC = () => {
  const navigate = useNavigate();
  const { createEvent, isLoading, error } = useEventStore();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(''); // Store as string, ensure correct format for backend
  const [time, setTime] = useState('');
  const [location, setLocation] = useState('');
  const [maxParticipants, setMaxParticipants] = useState(50);
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!title || !description || !date || !time || !location || maxParticipants <= 0) {
      setFormError('All fields are required and max participants must be positive.');
      return;
    }

    // Combine date and time into an ISO 8601 string or the format your backend expects.
    // Example: "YYYY-MM-DDTHH:MM:SSZ"
    // This needs careful handling to match backend expectations and timezones.
    // For simplicity, assuming date is YYYY-MM-DD and time is HH:MM
    const dateTimeString = `${date}T${time}:00`; // Add seconds if needed, consider timezone

    const eventData: CreateEventData = {
      title,
      description,
      date: dateTimeString,
      location,
      max_participants: Number(maxParticipants),
    };

    const newEvent = await createEvent(eventData);

    if (newEvent) {
      // toast.success('Event created successfully!');
      navigate(`/events/${newEvent.id}`); // Navigate to the new event's detail page
    } else {
      setFormError(error || 'Failed to create event. Please try again.');
      // toast.error(error || 'Failed to create event. Please try again.');
    }
  };

  return (
    <div className="container mx-auto py-8">
      <Card className="w-full max-w-2xl mx-auto glass-card">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-white">Create a New Event</CardTitle>
          <CardDescription className="text-gray-300">
            Fill in the details below to organize your next community gathering.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-gray-200">Event Title</Label>
              <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description" className="text-gray-200">Description</Label>
              <Textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} required rows={4} className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="date" className="text-gray-200">Date</Label>
                <Input id="date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required className="bg-white/10 border-white/20 text-white"/>
              </div>
              <div className="space-y-2">
                <Label htmlFor="time" className="text-gray-200">Time</Label>
                <Input id="time" type="time" value={time} onChange={(e) => setTime(e.target.value)} required className="bg-white/10 border-white/20 text-white"/>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location" className="text-gray-200">Location</Label>
              <Input id="location" value={location} onChange={(e) => setLocation(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxParticipants" className="text-gray-200">Max Participants</Label>
              <Input id="maxParticipants" type="number" value={maxParticipants} onChange={(e) => setMaxParticipants(Number(e.target.value))} min="1" required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>

            {formError && <p className="text-sm text-red-400 text-center">{formError}</p>}

            <div className="flex justify-end gap-4 pt-4">
              <Button type="button" variant="outline" onClick={() => navigate('/events')} className="btn-glass" disabled={isLoading}>
                Cancel
              </Button>
              <Button type="submit" className="btn-aurora" disabled={isLoading}>
                {isLoading ? 'Creating Event...' : 'Create Event'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateEventPage;
