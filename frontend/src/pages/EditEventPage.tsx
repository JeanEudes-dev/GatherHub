import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useEventStore } from '../store/eventStore'
import type { UpdateEventData, Event } from '../services/eventService'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Textarea } from '../components/ui/textarea'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
// import { toast } from 'sonner';
import { useAuthStore } from '../store/authStore' // To check if user is creator

const EditEventPage: React.FC = () => {
  const navigate = useNavigate()
  const { eventId } = useParams<{ eventId: string }>()
  const { currentEvent, fetchEventById, updateEvent, isLoading, error } =
    useEventStore()
  const { user: currentUser } = useAuthStore()

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [location, setLocation] = useState('')
  const [maxParticipants, setMaxParticipants] = useState(50)
  const [formError, setFormError] = useState<string | null>(null)
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null) // null = loading, false = unauthorized, true = authorized

  const populateForm = useCallback((event: Event | null) => {
    if (event) {
      setTitle(event.title)
      setDescription(event.description)
      // Split ISO datetime string for date and time inputs
      // Example: "2024-01-01T12:00:00Z" -> date: "2024-01-01", time: "12:00"
      // This needs to be robust for different datetime formats and timezones.
      if (event.date) {
        try {
          const d = new Date(event.date)
          const year = d.getFullYear()
          const month = `0${d.getMonth() + 1}`.slice(-2)
          const day = `0${d.getDate()}`.slice(-2)
          const hours = `0${d.getHours()}`.slice(-2)
          const minutes = `0${d.getMinutes()}`.slice(-2)
          setDate(`${year}-${month}-${day}`)
          setTime(`${hours}:${minutes}`)
        } catch (e) {
          console.error('Error parsing event date for form:', e)
          // Fallback or set to empty if parsing fails
          setDate('')
          setTime('')
        }
      } else {
        setDate('')
        setTime('')
      }
      setLocation(event.location)
      setMaxParticipants(event.max_participants)
    }
  }, [])

  useEffect(() => {
    if (eventId) {
      fetchEventById(Number(eventId)).then(eventData => {
        if (eventData && currentUser) {
          if (eventData.creator.id !== currentUser.id) {
            // toast.error("You are not authorized to edit this event.");
            setIsAuthorized(false)
            // navigate(`/events/${eventId}`); // Or to an unauthorized page
          } else {
            setIsAuthorized(true)
            populateForm(eventData)
          }
        } else if (!eventData) {
          // toast.error("Event not found.");
          setIsAuthorized(false) // Or handle as not found
          // navigate('/events');
        }
      })
    }
  }, [eventId, fetchEventById, populateForm, currentUser, navigate])

  // If currentEvent from store updates (e.g. by another component or WebSocket), repopulate
  useEffect(() => {
    if (currentEvent && currentEvent.id === Number(eventId) && isAuthorized) {
      populateForm(currentEvent)
    }
  }, [currentEvent, eventId, populateForm, isAuthorized])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)
    if (!isAuthorized) {
      setFormError('You are not authorized to perform this action.')
      return
    }

    if (
      !title ||
      !description ||
      !date ||
      !time ||
      !location ||
      maxParticipants <= 0
    ) {
      setFormError(
        'All fields are required and max participants must be positive.'
      )
      return
    }
    if (!eventId) {
      setFormError('Event ID is missing.')
      return
    }

    const dateTimeString = `${date}T${time}:00` // Add seconds if needed

    const eventData: UpdateEventData = {
      title,
      description,
      date: dateTimeString,
      location,
      max_participants: Number(maxParticipants),
    }

    const updated = await updateEvent(Number(eventId), eventData)

    if (updated) {
      // toast.success('Event updated successfully!');
      navigate(`/events/${eventId}`)
    } else {
      setFormError(error || 'Failed to update event. Please try again.')
      // toast.error(error || 'Failed to update event. Please try again.');
    }
  }

  if (isLoading && isAuthorized === null) {
    // Show loading only on initial fetch and auth check
    return <div className="py-10 text-center">Loading event details...</div>
  }

  if (isAuthorized === false) {
    return (
      <div className="container mx-auto py-8 text-center">
        <Card className="glass-card mx-auto w-full max-w-md p-8">
          <CardTitle className="text-2xl text-red-400">
            Not Authorized
          </CardTitle>
          <CardDescription className="mt-2 text-gray-300">
            You do not have permission to edit this event.
          </CardDescription>
          <Button
            onClick={() => navigate(eventId ? `/events/${eventId}` : '/events')}
            className="btn-aurora mt-6"
          >
            Back to Event
          </Button>
        </Card>
      </div>
    )
  }

  if (!currentEvent && !isLoading) {
    // Event not found after loading attempt
    return (
      <div className="py-10 text-center text-red-400">
        Event not found or could not be loaded.
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <Card className="glass-card mx-auto w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-white">
            Edit Event
          </CardTitle>
          <CardDescription className="text-gray-300">
            Update the details for your event.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-gray-200">
                Event Title
              </Label>
              <Input
                id="title"
                value={title}
                onChange={e => setTitle(e.target.value)}
                required
                className="border-white/20 bg-white/10 text-white placeholder-gray-400"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description" className="text-gray-200">
                Description
              </Label>
              <Textarea
                id="description"
                value={description}
                onChange={e => setDescription(e.target.value)}
                required
                rows={4}
                className="border-white/20 bg-white/10 text-white placeholder-gray-400"
              />
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="date" className="text-gray-200">
                  Date
                </Label>
                <Input
                  id="date"
                  type="date"
                  value={date}
                  onChange={e => setDate(e.target.value)}
                  required
                  className="border-white/20 bg-white/10 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="time" className="text-gray-200">
                  Time
                </Label>
                <Input
                  id="time"
                  type="time"
                  value={time}
                  onChange={e => setTime(e.target.value)}
                  required
                  className="border-white/20 bg-white/10 text-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location" className="text-gray-200">
                Location
              </Label>
              <Input
                id="location"
                value={location}
                onChange={e => setLocation(e.target.value)}
                required
                className="border-white/20 bg-white/10 text-white placeholder-gray-400"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxParticipants" className="text-gray-200">
                Max Participants
              </Label>
              <Input
                id="maxParticipants"
                type="number"
                value={maxParticipants}
                onChange={e => setMaxParticipants(Number(e.target.value))}
                min="1"
                required
                className="border-white/20 bg-white/10 text-white placeholder-gray-400"
              />
            </div>

            {formError && (
              <p className="text-center text-sm text-red-400">{formError}</p>
            )}
            {error && !formError && (
              <p className="text-center text-sm text-red-400">
                Store error: {error}
              </p>
            )}

            <div className="flex justify-end gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  navigate(eventId ? `/events/${eventId}` : '/events')
                }
                className="btn-glass"
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" className="btn-aurora" disabled={isLoading}>
                {isLoading ? 'Saving Changes...' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default EditEventPage
