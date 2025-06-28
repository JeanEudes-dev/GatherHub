/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useEventStore } from '../store/eventStore'
import type { Event } from '../services/eventService'
import { Button } from '../components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Input } from '../components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select'
import { motion } from 'framer-motion'

// Helper for date formatting
const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  } catch (error) {
    console.error('Failed to parse date:', dateString, error)
    return dateString // Fallback to original string
  }
}

const EventListPage: React.FC = () => {
  const { events, isLoading, error, pagination, fetchEvents } = useEventStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('') // e.g., 'upcoming', 'ongoing', 'completed'
  // Add more filters as needed: date_from, date_to, creator

  const loadEvents = useCallback(
    (page?: number, search?: string, status?: string) => {
      const params: Record<string, any> = {
        page: page || pagination.currentPage,
      }
      if (search) params.search = search
      if (status) params.status = status
      fetchEvents(params)
    },
    [fetchEvents, pagination.currentPage]
  )

  useEffect(() => {
    loadEvents(1, searchTerm, statusFilter) // Load initial page or on filter change
  }, [loadEvents, searchTerm, statusFilter]) // Removed pagination.currentPage to avoid loop with loadEvents

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value)
  }

  const handleStatusChange = (value: string) => {
    setStatusFilter(value)
  }

  const handlePageChange = (newPage: number) => {
    loadEvents(newPage, searchTerm, statusFilter)
  }

  // const handleDeleteEvent = async (eventId: number) => {
  //   const confirmed = window.confirm("Are you sure you want to delete this event?");
  //   if (confirmed) {
  //     const success = await deleteEvent(eventId)
  //     if (success) toast.success("Event deleted successfully.");
  //     else toast.error(useEventStore.getState().error || "Failed to delete event.");
  //   }
  // }

  if (isLoading && events.length === 0) {
    return <div className="py-10 text-center">Loading events...</div>
  }

  if (error) {
    return (
      <div className="py-10 text-center text-red-400">
        Error loading events: {error}
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex flex-col items-center justify-between gap-4 sm:flex-row">
        <h1 className="bg-gradient-to-r from-aurora-blue via-aurora-purple to-aurora-pink bg-clip-text text-4xl font-bold text-transparent">
          Community Events
        </h1>
        <Button asChild className="btn-aurora">
          <Link to="/events/new">Create New Event</Link>
        </Button>
      </div>

      {/* Filters and Search */}
      <div className="glass-card mb-6 rounded-lg p-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Input
            type="text"
            placeholder="Search events..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="border-white/20 bg-white/10 text-white placeholder-gray-400"
          />
          <Select value={statusFilter} onValueChange={handleStatusChange}>
            <SelectTrigger className="border-white/20 bg-white/10 text-white">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent className="border-gray-700 bg-gray-800 text-white">
              <SelectItem value="" className="hover:bg-gray-700">
                All Statuses
              </SelectItem>
              <SelectItem value="upcoming" className="hover:bg-gray-700">
                Upcoming
              </SelectItem>
              <SelectItem value="ongoing" className="hover:bg-gray-700">
                Ongoing
              </SelectItem>
              <SelectItem value="completed" className="hover:bg-gray-700">
                Completed
              </SelectItem>
            </SelectContent>
          </Select>
          {/* Add more filters here if needed */}
        </div>
      </div>

      {isLoading && <p className="my-4 text-center">Updating event list...</p>}

      {events.length === 0 && !isLoading ? (
        <div className="glass-card rounded-lg py-10 text-center">
          <h2 className="mb-2 text-2xl font-semibold text-white">
            No Events Found
          </h2>
          <p className="text-gray-400">
            Try adjusting your search or filters, or create a new event!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {events.map((event: Event, index: number) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <Card className="glass-card flex h-full flex-col">
                <CardHeader>
                  <CardTitle className="text-2xl font-bold text-white transition-colors hover:text-aurora-purple">
                    <Link to={`/events/${event.id}`}>{event.title}</Link>
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    By: {event.creator.first_name || event.creator.username}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="mb-3 h-20 overflow-hidden text-ellipsis text-gray-300">
                    {event.description}
                  </p>
                  <div className="space-y-1 text-sm text-gray-400">
                    <p>
                      <strong>Date:</strong> {formatDate(event.date)}
                    </p>
                    <p>
                      <strong>Location:</strong> {event.location}
                    </p>
                    <p>
                      <strong>Status:</strong>{' '}
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs capitalize ${
                          event.status === 'upcoming'
                            ? 'bg-blue-500/20 text-blue-300'
                            : event.status === 'ongoing'
                              ? 'bg-green-500/20 text-green-300'
                              : 'bg-gray-500/20 text-gray-300'
                        }`}
                      >
                        {event.status}
                      </span>
                    </p>
                    <p>
                      <strong>Participants:</strong>{' '}
                      {event.current_participants} / {event.max_participants}
                    </p>
                  </div>
                </CardContent>
                <CardFooter className="mt-auto flex items-center justify-between">
                  <Button
                    variant="ghost"
                    asChild
                    className="text-aurora-blue hover:bg-aurora-blue/10"
                  >
                    <Link to={`/events/${event.id}`}>View Details</Link>
                  </Button>
                  {/* Placeholder for Edit/Delete based on permissions */}
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {pagination.count > pagination.pageSize && (
        <div className="mt-8 flex items-center justify-center space-x-2">
          <Button
            onClick={() => handlePageChange(pagination.currentPage - 1)}
            disabled={!pagination.previous || isLoading}
            variant="outline"
            className="btn-glass"
          >
            Previous
          </Button>
          <span className="text-gray-300">
            Page {pagination.currentPage} of{' '}
            {Math.ceil(pagination.count / pagination.pageSize)}
          </span>
          <Button
            onClick={() => handlePageChange(pagination.currentPage + 1)}
            disabled={!pagination.next || isLoading}
            variant="outline"
            className="btn-glass"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}

export default EventListPage
