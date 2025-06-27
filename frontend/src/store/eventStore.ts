import { create } from 'zustand';
import {
  listEvents as apiListEvents,
  createEvent as apiCreateEvent,
  getEventDetails as apiGetEventDetails,
  updateEvent as apiUpdateEvent,
  deleteEvent as apiDeleteEvent,
  joinEvent as apiJoinEvent,
  leaveEvent as apiLeaveEvent,
  Event,
  CreateEventData,
  UpdateEventData,
  PaginatedEventsResponse
} from '../services/eventService';
// import { useAuthStore } from './authStore'; // For handling auth errors

// Define the state structure for events
interface EventState {
  events: Event[];
  currentEvent: Event | null;
  isLoading: boolean;
  error: string | null;
  pagination: {
    count: number;
    next: string | null;
    previous: string | null;
    currentPage: number;
    pageSize: number; // You might want to control this
  };

  // Actions
  fetchEvents: (params?: Record<string, any>) => Promise<void>;
  fetchEventById: (eventId: number) => Promise<Event | null>;
  createEvent: (eventData: CreateEventData) => Promise<Event | null>;
  updateEvent: (eventId: number, eventData: UpdateEventData) => Promise<Event | null>;
  deleteEvent: (eventId: number) => Promise<boolean>;
  joinEvent: (eventId: number) => Promise<boolean>;
  leaveEvent: (eventId: number) => Promise<boolean>;

  // Real-time updates (placeholders, to be called by WebSocket handlers)
  handleEventCreated: (event: Event) => void;
  handleEventUpdated: (event: Event) => void;
  handleEventDeleted: (eventId: number) => void;
  handleParticipantChange: (eventId: number, change: { current_participants: number, newParticipant?: any, removedParticipant?: any }) => void;
}

export const useEventStore = create<EventState>((set, get) => ({
  events: [],
  currentEvent: null,
  isLoading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 10, // Default page size
  },

  fetchEvents: async (params?: Record<string, any>) => {
    set({ isLoading: true, error: null });
    const page = params?.page || get().pagination.currentPage;
    const pageSize = params?.page_size || get().pagination.pageSize;

    try {
      const response: PaginatedEventsResponse = await apiListEvents({ ...params, page, page_size: pageSize });
      set({
        events: response.results,
        pagination: {
          ...get().pagination,
          count: response.count,
          next: response.next,
          previous: response.previous,
          currentPage: page,
        },
        isLoading: false,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch events';
      set({ isLoading: false, error: errorMessage });
      // if (error.response?.status === 401) useAuthStore.getState().logout();
    }
  },

  fetchEventById: async (eventId: number) => {
    set({ isLoading: true, error: null });
    try {
      const event = await apiGetEventDetails(eventId);
      set({ currentEvent: event, isLoading: false });
      // Also update this event in the main list if it exists
      set(state => ({
        events: state.events.map(e => e.id === eventId ? event : e)
      }));
      return event;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch event details';
      set({ isLoading: false, error: errorMessage, currentEvent: null });
      return null;
    }
  },

  createEvent: async (eventData: CreateEventData) => {
    set({ isLoading: true, error: null });
    try {
      const newEvent = await apiCreateEvent(eventData);
      set(state => ({
        // events: [newEvent, ...state.events], // Add to start, or refetch
        isLoading: false,
      }));
      await get().fetchEvents({ page: 1 }); // Refetch to get the latest list with pagination
      return newEvent;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create event';
      set({ isLoading: false, error: errorMessage });
      return null;
    }
  },

  updateEvent: async (eventId: number, eventData: UpdateEventData) => {
    set({ isLoading: true, error: null });
    try {
      const updatedEvent = await apiUpdateEvent(eventId, eventData);
      set(state => ({
        events: state.events.map(event => event.id === eventId ? updatedEvent : event),
        currentEvent: state.currentEvent?.id === eventId ? updatedEvent : state.currentEvent,
        isLoading: false,
      }));
      return updatedEvent;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update event';
      set({ isLoading: false, error: errorMessage });
      return null;
    }
  },

  deleteEvent: async (eventId: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiDeleteEvent(eventId);
      set(state => ({
        events: state.events.filter(event => event.id !== eventId),
        currentEvent: state.currentEvent?.id === eventId ? null : state.currentEvent,
        isLoading: false,
      }));
      // Adjust pagination if needed or refetch current page
      if (get().events.length === 0 && get().pagination.currentPage > 1) {
        await get().fetchEvents({ page: get().pagination.currentPage - 1});
      } else {
         await get().fetchEvents({ page: get().pagination.currentPage });
      }
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete event';
      set({ isLoading: false, error: errorMessage });
      return false;
    }
  },

  joinEvent: async (eventId: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiJoinEvent(eventId);
      // Optimistically update or refetch event details
      const updatedEvent = await apiGetEventDetails(eventId); // Refetch for accurate participant count
      set(state => ({
        events: state.events.map(event => event.id === eventId ? updatedEvent : event),
        currentEvent: state.currentEvent?.id === eventId ? updatedEvent : state.currentEvent,
        isLoading: false,
      }));
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to join event';
      set({ isLoading: false, error: errorMessage });
      return false;
    }
  },

  leaveEvent: async (eventId: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiLeaveEvent(eventId);
      // Optimistically update or refetch event details
      const updatedEvent = await apiGetEventDetails(eventId); // Refetch
      set(state => ({
        events: state.events.map(event => event.id === eventId ? updatedEvent : event),
        currentEvent: state.currentEvent?.id === eventId ? updatedEvent : state.currentEvent,
        isLoading: false,
      }));
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to leave event';
      set({ isLoading: false, error: errorMessage });
      return false;
    }
  },

  // WebSocket Handlers
  handleEventCreated: (newEvent: Event) => {
    // Check if event already exists to prevent duplicates if also received via normal API call
    if (!get().events.find(event => event.id === newEvent.id)) {
      set(state => ({
        events: [newEvent, ...state.events.slice(0, state.pagination.pageSize -1)], // Add to start, maintain page size
        pagination: { ...state.pagination, count: state.pagination.count + 1 }
      }));
      // Potentially refetch if this causes pagination issues or sort order is critical
    }
  },

  handleEventUpdated: (updatedEvent: Event) => {
    set(state => ({
      events: state.events.map(event => event.id === updatedEvent.id ? updatedEvent : event),
      currentEvent: state.currentEvent?.id === updatedEvent.id ? updatedEvent : state.currentEvent,
    }));
  },

  handleEventDeleted: (eventId: number) => {
    set(state => ({
      events: state.events.filter(event => event.id !== eventId),
      currentEvent: state.currentEvent?.id === eventId ? null : state.currentEvent,
      pagination: { ...state.pagination, count: Math.max(0, state.pagination.count - 1) }
    }));
    // Potentially refetch current page if an item from it was deleted
  },

  handleParticipantChange: (eventId: number, change: { current_participants: number }) => {
    set(state => ({
      events: state.events.map(event =>
        event.id === eventId ? { ...event, current_participants: change.current_participants } : event
      ),
      currentEvent: state.currentEvent?.id === eventId
        ? { ...state.currentEvent, current_participants: change.current_participants }
        : state.currentEvent,
    }));
  },

}));
