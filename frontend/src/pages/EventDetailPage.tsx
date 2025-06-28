/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useState, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useEventStore } from '../store/eventStore'
import { useAuthStore } from '../store/authStore'
import type { EventParticipant } from '../services/eventService'
import { Button } from '../components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import TaskList from '../features/tasks/TaskList'
import VoteList from '../features/voting/VoteList' // Import VoteList
import toast from 'react-hot-toast'

// Helper for date formatting (consider moving to a utils file)
const formatDate = (dateString: string, includeTime = true) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }
    if (includeTime) {
      options.hour = '2-digit'
      options.minute = '2-digit'
    }
    return date.toLocaleDateString(undefined, options)
  } catch (error) {
    console.error('Failed to parse date:', dateString, error)
    return dateString
  }
}

const EventDetailPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>()
  const navigate = useNavigate()
  const {
    currentEvent,
    fetchEventById,
    isLoading,
    error,
    joinEvent,
    leaveEvent,
    deleteEvent: storeDeleteEvent,
  } = useEventStore()
  const { user: currentUser, isAuthenticated } = useAuthStore()

  // Local loading state for actions like join/leave/delete to provide instant feedback
  const [isActionLoading, setIsActionLoading] = useState(false)

  useEffect(() => {
    if (eventId) {
      fetchEventById(Number(eventId))
    }
  }, [eventId, fetchEventById])

  const isUserParticipant = useMemo(() => {
    if (!currentUser || !currentEvent || !currentEvent.participants)
      return false
    return currentEvent.participants.some(p => p.id === currentUser.id)
  }, [currentUser, currentEvent])

  const isUserCreator = useMemo(() => {
    if (!currentUser || !currentEvent) return false
    return currentEvent.creator.id === currentUser.id
  }, [currentUser, currentEvent])

  const handleJoinEvent = async () => {
    if (!eventId || !isAuthenticated()) {
      // toast.error("You must be logged in to join an event.");
      navigate('/login')
      return
    }
    setIsActionLoading(true)
    const success = await joinEvent(Number(eventId))
    if (success) toast.success('Successfully joined the event!')
    else
      toast.error(useEventStore.getState().error || 'Failed to join the event.')
    setIsActionLoading(false)
  }

  const handleLeaveEvent = async () => {
    if (!eventId) return
    setIsActionLoading(true)
    const success = await leaveEvent(Number(eventId))
    if (success) toast.success('Successfully left the event!')
    else
      toast.error(
        useEventStore.getState().error || 'Failed to leave the event.'
      )
    setIsActionLoading(false)
  }

  const handleDeleteEvent = async () => {
    if (!eventId || !isUserCreator) return
    const confirmed = window.confirm(
      'Are you sure you want to delete this event? This action cannot be undone.'
    )
    if (confirmed) {
      setIsActionLoading(true)
      const success = await storeDeleteEvent(Number(eventId))
      if (success) {
        toast.success('Event deleted successfully!')
        navigate('/events')
      } else {
        toast.error(useEventStore.getState().error || 'Failed to delete event.')
      }
      setIsActionLoading(false)
    }
  }

  if (isLoading && !currentEvent) {
    return <div className="py-10 text-center">Loading event details...</div>
  }

  if (error && !currentEvent) {
    // Show error if event couldn't be fetched at all
    return <div className="py-10 text-center text-red-400">Error: {error}</div>
  }

  if (!currentEvent) {
    return (
      <div className="py-10 text-center text-gray-400">Event not found.</div>
    )
  }

  // Determine if event date is in the past (for join/leave logic if needed)

  return (
    <div className="container mx-auto py-8">
      <Card className="glass-card mx-auto w-full max-w-4xl">
        <CardHeader className="pb-4">
          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row">
            <div>
              <CardTitle className="mb-2 text-4xl font-bold text-white">
                {currentEvent.title}
              </CardTitle>
              <CardDescription className="text-lg text-gray-300">
                Organized by:{' '}
                <Link
                  to={`/users/${currentEvent.creator.username}`}
                  className="text-aurora-blue hover:underline"
                >
                  {currentEvent.creator.first_name ||
                    currentEvent.creator.username}
                </Link>
              </CardDescription>
            </div>
            {isUserCreator && (
              <div className="mt-2 flex flex-shrink-0 gap-2 sm:mt-0">
                <Button
                  variant="outline"
                  size="sm"
                  asChild
                  className="btn-glass"
                >
                  <Link to={`/events/edit/${currentEvent.id}`}>Edit Event</Link>
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDeleteEvent}
                  disabled={isActionLoading}
                >
                  {isActionLoading && currentEvent.id.toString() === eventId
                    ? 'Deleting...'
                    : 'Delete Event'}
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 gap-6 text-sm md:grid-cols-3">
            <div className="glass-card rounded-md p-4">
              <h3 className="mb-1 font-semibold text-gray-200">Date & Time</h3>
              <p className="text-aurora-green">
                {formatDate(currentEvent.date)}
              </p>
            </div>
            <div className="glass-card rounded-md p-4">
              <h3 className="mb-1 font-semibold text-gray-200">Location</h3>
              <p className="text-aurora-yellow">{currentEvent.location}</p>
            </div>
            <div className="glass-card rounded-md p-4">
              <h3 className="mb-1 font-semibold text-gray-200">
                Status & Capacity
              </h3>
              <p className="capitalize text-aurora-pink">
                {currentEvent.status}
              </p>
              <p className="text-gray-400">
                {currentEvent.current_participants} /{' '}
                {currentEvent.max_participants} participants
              </p>
            </div>
          </div>

          <div>
            <h3 className="mb-2 text-xl font-semibold text-white">
              About this Event
            </h3>
            <p className="whitespace-pre-wrap leading-relaxed text-gray-300">
              {currentEvent.description}
            </p>
          </div>

          {/* Action Buttons: Join/Leave */}
          {isAuthenticated() && !isUserCreator && (
            <div className="pt-4">
              {isUserParticipant ? (
                <Button
                  onClick={handleLeaveEvent}
                  className="btn-aurora w-full bg-red-500 hover:bg-red-600 sm:w-auto"
                  disabled={isActionLoading /*|| isEventPast*/}
                >
                  {isActionLoading ? 'Leaving...' : 'Leave Event'}
                </Button>
              ) : currentEvent.current_participants <
                currentEvent.max_participants ? (
                <Button
                  onClick={handleJoinEvent}
                  className="btn-aurora w-full sm:w-auto"
                  disabled={isActionLoading /*|| isEventPast*/}
                >
                  {isActionLoading ? 'Joining...' : 'Join Event'}
                </Button>
              ) : (
                <Button className="w-full sm:w-auto" disabled={true}>
                  Event Full
                </Button>
              )}
            </div>
          )}
          {!isAuthenticated() && (
            <div className="pt-4 text-center">
              <p className="mb-2 text-gray-400">
                You need to be logged in to join this event.
              </p>
              <Button asChild className="btn-aurora">
                <Link to={`/login?redirect=/events/${eventId}`}>
                  Login to Join
                </Link>
              </Button>
            </div>
          )}

          {/* Participants List */}
          {currentEvent.participants &&
            currentEvent.participants.length > 0 && (
              <div>
                <h3 className="mb-3 text-xl font-semibold text-white">
                  Participants ({currentEvent.current_participants})
                </h3>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                  {currentEvent.participants.map(
                    (participant: EventParticipant) => (
                      <Link
                        key={participant.id}
                        to={`/users/${participant.username}`}
                        className="group text-center"
                      >
                        <Avatar className="mx-auto mb-1 h-16 w-16 border-2 border-transparent transition-all group-hover:border-aurora-purple">
                          <AvatarImage
                            src={(participant as any).avatar || undefined}
                            alt={participant.username}
                          />
                          <AvatarFallback>
                            {participant.first_name
                              ? participant.first_name.charAt(0)
                              : participant.username.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <p className="truncate text-sm text-gray-300 group-hover:text-aurora-purple">
                          {participant.first_name || participant.username}
                        </p>
                      </Link>
                    )
                  )}
                </div>
              </div>
            )}

          {/* Tasks Section */}
          <div className="pt-6">
            <TaskList
              eventId={currentEvent.id}
              eventParticipants={(currentEvent.participants || []).map(p => ({
                ...p,
                is_admin: (p as any).is_admin ?? false,
                is_moderator: (p as any).is_moderator ?? false,
                email: (p as any).email, // preserve email if present
              }))}
              isEventCreator={isUserCreator}
            />
          </div>

          {/* Voting Section */}
          <div className="pt-6">
            <VoteList
              eventId={currentEvent.id}
              isEventCreator={isUserCreator}
            />
          </div>
        </CardContent>
        <CardFooter className="text-center">
          <Button
            variant="outline"
            onClick={() => navigate('/events')}
            className="btn-glass"
          >
            Back to All Events
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

export default EventDetailPage
