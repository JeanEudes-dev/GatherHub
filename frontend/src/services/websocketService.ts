import { useEventStore } from '../store/eventStore'
import { useTaskStore } from '../store/taskStore'
import { useVotingStore } from '../store/votingStore' // Import voting store

const WS_BASE_URL = import.meta.env.VITE_WS_URL
  ? `${import.meta.env.VITE_WS_URL}/ws`
  : 'ws://localhost:8000/ws'

let eventSocket: WebSocket | null = null
let taskSocket: WebSocket | null = null
let votingSocket: WebSocket | null = null

function connectEventSocket() {
  // const { accessToken } = useAuthStore.getState(); // If needed for auth
  const eventUrl = `${WS_BASE_URL}/events/`

  if (
    eventSocket &&
    eventSocket.readyState !== WebSocket.CLOSED &&
    eventSocket.readyState !== WebSocket.CLOSING
  ) {
    console.log('Event WebSocket already connected or connecting.')
    return
  }

  eventSocket = new WebSocket(eventUrl)

  eventSocket.onopen = () => console.log('Event WebSocket connected')
  eventSocket.onmessage = event => {
    try {
      const message = JSON.parse(event.data as string)
      console.log('Event WS message:', message)
      const store = useEventStore.getState()
      switch (message.type) {
        case 'event_created':
          store.handleEventCreated(message.data)
          break
        case 'event_updated':
          store.handleEventUpdated(message.data)
          break
        case 'event_deleted':
          store.handleEventDeleted(message.data.event_id)
          break
        case 'event_joined':
        case 'event_left':
          store.handleParticipantChange(message.data.event_id, {
            current_participants: message.data.current_participants,
          })
          break
        default:
          console.warn('Unknown Event WS message type:', message.type)
      }
    } catch (error) {
      console.error('Error processing Event WS message:', error)
    }
  }
  eventSocket.onclose = e =>
    console.log('Event WebSocket disconnected:', e.reason, e.code)
  eventSocket.onerror = error => {
    console.error('Event WebSocket error:', error)
    eventSocket?.close()
  }
}

function connectTaskSocket() {
  const taskUrl = `${WS_BASE_URL}/tasks/`

  if (
    taskSocket &&
    taskSocket.readyState !== WebSocket.CLOSED &&
    taskSocket.readyState !== WebSocket.CLOSING
  ) {
    console.log('Task WebSocket already connected or connecting.')
    return
  }

  taskSocket = new WebSocket(taskUrl)

  taskSocket.onopen = () => console.log('Task WebSocket connected')
  taskSocket.onmessage = event => {
    try {
      const message = JSON.parse(event.data as string)
      console.log('Task WS message:', message)
      const store = useTaskStore.getState()
      switch (message.type) {
        case 'task_created':
          store.handleTaskCreated(message.data)
          break
        case 'task_updated':
          store.handleTaskUpdated(message.data)
          break
        case 'task_deleted':
          store.handleTaskDeleted(message.data.task_id, message.data.event_id)
          break
        default:
          console.warn('Unknown Task WS message type:', message.type)
      }
    } catch (error) {
      console.error('Error processing Task WS message:', error)
    }
  }
  taskSocket.onclose = e =>
    console.log('Task WebSocket disconnected:', e.reason, e.code)
  taskSocket.onerror = error => {
    console.error('Task WebSocket error:', error)
    taskSocket?.close()
  }
}

function connectVotingSocket() {
  const votingUrl = `${WS_BASE_URL}/voting/`

  if (
    votingSocket &&
    votingSocket.readyState !== WebSocket.CLOSED &&
    votingSocket.readyState !== WebSocket.CLOSING
  ) {
    console.log('Voting WebSocket already connected or connecting.')
    return
  }

  votingSocket = new WebSocket(votingUrl)

  votingSocket.onopen = () => console.log('Voting WebSocket connected')
  votingSocket.onmessage = event => {
    try {
      const message = JSON.parse(event.data as string)
      console.log('Voting WS message:', message)
      const store = useVotingStore.getState()
      // Expected message types from backend README: vote_created, vote_cast, vote_results_updated, vote_ended
      switch (message.type) {
        case 'vote_created':
          store.handleVoteCreated(message.data)
          break
        case 'vote_cast': // This usually triggers an update to the vote itself (total_votes, user_voted status)
          // And potentially an update to results.
          store.handleVoteUpdated(message.data.vote) // Assuming backend sends updated vote object
          if (message.data.results)
            store.handleVoteResultsUpdated(message.data.results)
          break
        case 'vote_results_updated':
          store.handleVoteResultsUpdated(message.data)
          break
        case 'vote_ended':
          store.handleVoteUpdated(message.data)
          break // Assuming data is the full vote object with status 'ended'
        default:
          console.warn('Unknown Voting WS message type:', message.type)
      }
    } catch (error) {
      console.error('Error processing Voting WS message:', error)
    }
  }
  votingSocket.onclose = e =>
    console.log('Voting WebSocket disconnected:', e.reason, e.code)
  votingSocket.onerror = error => {
    console.error('Voting WebSocket error:', error)
    votingSocket?.close()
  }
}

function disconnectEventSocket() {
  if (eventSocket) {
    eventSocket.close()
    eventSocket = null
    console.log('Event WebSocket disconnected by client.')
  }
}

function disconnectTaskSocket() {
  if (taskSocket) {
    taskSocket.close()
    taskSocket = null
    console.log('Task WebSocket disconnected by client.')
  }
}

function disconnectVotingSocket() {
  if (votingSocket) {
    votingSocket.close()
    votingSocket = null
    console.log('Voting WebSocket disconnected by client.')
  }
}

// Initialize WebSocket connections
export const initializeWebSockets = () => {
  console.log('Attempting to initialize WebSockets...')
  connectEventSocket()
  connectTaskSocket()
  connectVotingSocket()
}

export const closeWebSockets = () => {
  console.log('Attempting to close WebSockets...')
  disconnectEventSocket()
  disconnectTaskSocket()
  disconnectVotingSocket()
}

export {
  connectEventSocket,
  disconnectEventSocket,
  connectTaskSocket,
  disconnectTaskSocket,
  connectVotingSocket,
  disconnectVotingSocket,
}
