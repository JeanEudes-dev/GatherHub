# GatherHub API Examples

## Complete API Usage Examples

This document provides comprehensive examples for all GatherHub API endpoints with practical use cases.

## Table of Contents

1. [Authentication Flow](#authentication-flow)
2. [Event Management](#event-management)
3. [Voting System](#voting-system)
4. [Task Management](#task-management)
5. [Real-time Features](#real-time-features)
6. [Error Handling](#error-handling)

## Authentication Flow

### Complete Registration and Login Flow

```javascript
class GatherHubAuth {
  constructor(baseURL = "http://localhost:8000/api/v1") {
    this.baseURL = baseURL;
    this.token = localStorage.getItem("access_token");
  }

  async register(userData) {
    const response = await fetch(`${this.baseURL}/auth/register/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (response.ok) {
      const data = await response.json();
      this.setTokens(data.tokens);
      return data.user;
    } else {
      const error = await response.json();
      throw new Error(JSON.stringify(error));
    }
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/token/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      const tokens = await response.json();
      this.setTokens(tokens);
      return tokens;
    } else {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }
  }

  setTokens(tokens) {
    localStorage.setItem("access_token", tokens.access);
    localStorage.setItem("refresh_token", tokens.refresh);
    this.token = tokens.access;
  }

  async getProfile() {
    const response = await this.authenticatedRequest("GET", "/profile/");
    return response;
  }

  async updateProfile(profileData) {
    const response = await this.authenticatedRequest(
      "PUT",
      "/profile/",
      profileData
    );
    return response;
  }

  async changePassword(currentPassword, newPassword) {
    const response = await this.authenticatedRequest(
      "POST",
      "/auth/password/change/",
      {
        current_password: currentPassword,
        new_password: newPassword,
      }
    );
    return response;
  }

  async authenticatedRequest(method, endpoint, data = null) {
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, options);

    if (response.status === 401) {
      // Try to refresh token
      const refreshed = await this.refreshToken();
      if (refreshed) {
        options.headers.Authorization = `Bearer ${this.token}`;
        return fetch(`${this.baseURL}${endpoint}`, options).then((r) =>
          r.json()
        );
      } else {
        this.logout();
        throw new Error("Authentication failed");
      }
    }

    return response.json();
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("access_token", data.access);
        this.token = data.access;
        return true;
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
    }

    return false;
  }

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    this.token = null;
  }
}

// Usage Example
const auth = new GatherHubAuth();

// Register new user
try {
  const user = await auth.register({
    email: "john.doe@example.com",
    password: "securepassword123",
    name: "John Doe",
  });
  console.log("Registered user:", user);
} catch (error) {
  console.error("Registration failed:", error.message);
}

// Login existing user
try {
  await auth.login("john.doe@example.com", "securepassword123");
  console.log("Login successful");

  // Get and update profile
  const profile = await auth.getProfile();
  console.log("User profile:", profile);

  await auth.updateProfile({ name: "John Smith" });
  console.log("Profile updated");
} catch (error) {
  console.error("Authentication error:", error.message);
}
```

## Event Management

### Complete Event Management Class

```javascript
class EventManager {
  constructor(auth) {
    this.auth = auth;
    this.baseURL = auth.baseURL;
  }

  async createEvent(eventData) {
    return this.auth.authenticatedRequest("POST", "/events/", eventData);
  }

  async getEvents(filters = {}) {
    const queryString = new URLSearchParams(filters).toString();
    const endpoint = `/events/${queryString ? "?" + queryString : ""}`;
    return this.auth.authenticatedRequest("GET", endpoint);
  }

  async getEvent(eventId) {
    return this.auth.authenticatedRequest("GET", `/events/${eventId}/`);
  }

  async updateEvent(eventId, eventData) {
    return this.auth.authenticatedRequest(
      "PUT",
      `/events/${eventId}/`,
      eventData
    );
  }

  async deleteEvent(eventId) {
    return this.auth.authenticatedRequest("DELETE", `/events/${eventId}/`);
  }

  async lockEvent(eventId) {
    return this.auth.authenticatedRequest("POST", `/events/${eventId}/lock/`);
  }

  async unlockEvent(eventId) {
    return this.auth.authenticatedRequest("POST", `/events/${eventId}/unlock/`);
  }

  async addTimeslot(eventId, timeslotData) {
    return this.auth.authenticatedRequest(
      "POST",
      `/events/${eventId}/timeslots/`,
      timeslotData
    );
  }

  async updateTimeslot(eventId, timeslotId, timeslotData) {
    return this.auth.authenticatedRequest(
      "PUT",
      `/events/${eventId}/timeslots/${timeslotId}/`,
      timeslotData
    );
  }

  async deleteTimeslot(eventId, timeslotId) {
    return this.auth.authenticatedRequest(
      "DELETE",
      `/events/${eventId}/timeslots/${timeslotId}/`
    );
  }
}

// Usage Examples
const eventManager = new EventManager(auth);

// Create a new event with multiple timeslots
const newEvent = await eventManager.createEvent({
  title: "Team Building Workshop",
  description: "Monthly team building activities and planning session",
  timeslots: [
    {
      start_time: "2024-01-15T14:00:00Z",
      end_time: "2024-01-15T16:00:00Z",
      description: "Monday afternoon session",
    },
    {
      start_time: "2024-01-16T10:00:00Z",
      end_time: "2024-01-16T12:00:00Z",
      description: "Tuesday morning session",
    },
    {
      start_time: "2024-01-17T15:00:00Z",
      end_time: "2024-01-17T17:00:00Z",
      description: "Wednesday afternoon session",
    },
  ],
});

console.log("Created event:", newEvent);

// Get all events with filtering
const events = await eventManager.getEvents({
  search: "workshop",
  ordering: "-created_at",
});

console.log(`Found ${events.count} events`);

// Get specific event details
const eventDetails = await eventManager.getEvent(newEvent.id);
console.log("Event details:", eventDetails);

// Add a new timeslot to existing event
const newTimeslot = await eventManager.addTimeslot(newEvent.id, {
  start_time: "2024-01-18T13:00:00Z",
  end_time: "2024-01-18T15:00:00Z",
  description: "Thursday afternoon session",
});

console.log("Added timeslot:", newTimeslot);
```

## Voting System

### Complete Voting Management

```javascript
class VotingManager {
  constructor(auth) {
    this.auth = auth;
    this.baseURL = auth.baseURL;
  }

  async vote(timeslotId) {
    return this.auth.authenticatedRequest("POST", "/voting/votes/", {
      timeslot: timeslotId,
    });
  }

  async updateVote(voteId, timeslotId) {
    return this.auth.authenticatedRequest("PUT", `/voting/votes/${voteId}/`, {
      timeslot: timeslotId,
    });
  }

  async deleteVote(voteId) {
    return this.auth.authenticatedRequest("DELETE", `/voting/votes/${voteId}/`);
  }

  async getVotes(eventId = null) {
    const endpoint = eventId
      ? `/voting/votes/?event=${eventId}`
      : "/voting/votes/";
    return this.auth.authenticatedRequest("GET", endpoint);
  }

  async getEventVotingResults(eventId) {
    return this.auth.authenticatedRequest(
      "GET",
      `/events/${eventId}/voting-results/`
    );
  }

  async bulkVote(timeslotIds) {
    const votes = timeslotIds.map((id) => ({ timeslot: id }));
    const results = [];

    for (const vote of votes) {
      try {
        const result = await this.vote(vote.timeslot);
        results.push({ success: true, data: result });
      } catch (error) {
        results.push({
          success: false,
          error: error.message,
          timeslot: vote.timeslot,
        });
      }
    }

    return results;
  }
}

// Usage Examples
const votingManager = new VotingManager(auth);

// Vote on multiple timeslots
const timeslotIds = [1, 3, 5];
const voteResults = await votingManager.bulkVote(timeslotIds);

voteResults.forEach((result, index) => {
  if (result.success) {
    console.log(`Vote ${index + 1} successful:`, result.data);
  } else {
    console.error(`Vote ${index + 1} failed:`, result.error);
  }
});

// Get voting results for an event
const votingResults = await votingManager.getEventVotingResults(1);
console.log("Voting results:", votingResults);

// Update a vote
try {
  const updatedVote = await votingManager.updateVote(1, 2);
  console.log("Vote updated:", updatedVote);
} catch (error) {
  console.error("Failed to update vote:", error);
}
```

## Task Management

### Complete Task Management

```javascript
class TaskManager {
  constructor(auth) {
    this.auth = auth;
    this.baseURL = auth.baseURL;
  }

  async createTask(taskData) {
    return this.auth.authenticatedRequest("POST", "/tasks/", taskData);
  }

  async getTasks(filters = {}) {
    const queryString = new URLSearchParams(filters).toString();
    const endpoint = `/tasks/${queryString ? "?" + queryString : ""}`;
    return this.auth.authenticatedRequest("GET", endpoint);
  }

  async getTask(taskId) {
    return this.auth.authenticatedRequest("GET", `/tasks/${taskId}/`);
  }

  async updateTask(taskId, taskData) {
    return this.auth.authenticatedRequest("PUT", `/tasks/${taskId}/`, taskData);
  }

  async updateTaskStatus(taskId, status) {
    return this.auth.authenticatedRequest("PATCH", `/tasks/${taskId}/`, {
      status,
    });
  }

  async assignTask(taskId, userId) {
    return this.auth.authenticatedRequest("PATCH", `/tasks/${taskId}/`, {
      assigned_to: userId,
    });
  }

  async deleteTask(taskId) {
    return this.auth.authenticatedRequest("DELETE", `/tasks/${taskId}/`);
  }

  async getTasksByEvent(eventId) {
    return this.getTasks({ event: eventId });
  }

  async getMyTasks() {
    return this.getTasks({ assigned_to: "me" });
  }

  async markTaskComplete(taskId) {
    return this.updateTaskStatus(taskId, "completed");
  }

  async addTaskComment(taskId, comment) {
    return this.auth.authenticatedRequest(
      "POST",
      `/tasks/${taskId}/comments/`,
      {
        content: comment,
      }
    );
  }
}

// Usage Examples
const taskManager = new TaskManager(auth);

// Create tasks for an event
const eventTasks = [
  {
    event: 1,
    title: "Book venue",
    description: "Find and book appropriate venue for the workshop",
    priority: "high",
    due_date: "2024-01-10T23:59:59Z",
  },
  {
    event: 1,
    title: "Prepare materials",
    description: "Create worksheets and presentation slides",
    priority: "medium",
    due_date: "2024-01-12T23:59:59Z",
  },
  {
    event: 1,
    title: "Send invitations",
    description: "Email invitations to all team members",
    priority: "high",
    due_date: "2024-01-08T23:59:59Z",
  },
];

const createdTasks = [];
for (const task of eventTasks) {
  try {
    const createdTask = await taskManager.createTask(task);
    createdTasks.push(createdTask);
    console.log("Created task:", createdTask.title);
  } catch (error) {
    console.error("Failed to create task:", task.title, error);
  }
}

// Get all my assigned tasks
const myTasks = await taskManager.getMyTasks();
console.log(`I have ${myTasks.count} assigned tasks`);

// Update task status
if (createdTasks.length > 0) {
  await taskManager.markTaskComplete(createdTasks[0].id);
  console.log("Marked first task as complete");
}

// Get tasks for specific event
const eventTasks = await taskManager.getTasksByEvent(1);
console.log(`Event has ${eventTasks.count} tasks`);
```

## Real-time Features

### WebSocket Integration

```javascript
class GatherHubWebSocket {
  constructor(auth) {
    this.auth = auth;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
  }

  connect() {
    const token = this.auth.token;
    const wsUrl = `ws://localhost:8000/ws/?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
      this.emit("connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      this.emit("disconnected");
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.emit("error", error);
    };
  }

  handleMessage(data) {
    const { type, payload } = data;

    switch (type) {
      case "vote_update":
        this.emit("voteUpdate", payload);
        break;
      case "task_update":
        this.emit("taskUpdate", payload);
        break;
      case "event_update":
        this.emit("eventUpdate", payload);
        break;
      default:
        console.log("Unknown message type:", type);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay =
        this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      console.log(
        `Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`
      );

      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error("Max reconnection attempts reached");
      this.emit("maxReconnectAttemptsReached");
    }
  }

  send(type, payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    } else {
      console.error("WebSocket is not connected");
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((callback) => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage Example
const ws = new GatherHubWebSocket(auth);

// Set up event listeners
ws.on("connected", () => {
  console.log("WebSocket connection established");
});

ws.on("voteUpdate", (data) => {
  console.log("Vote update received:", data);
  // Update UI with new vote data
  updateVoteDisplay(data.timeslot_id, data.vote_count);
});

ws.on("taskUpdate", (data) => {
  console.log("Task update received:", data);
  // Update task status in UI
  updateTaskStatus(data.task_id, data.status);
});

ws.on("eventUpdate", (data) => {
  console.log("Event update received:", data);
  // Refresh event data
  refreshEventDisplay(data.event_id);
});

// Connect to WebSocket
ws.connect();

// Send a message
ws.send("join_event", { event_id: 1 });
```

## Error Handling

### Comprehensive Error Handler

```javascript
class APIErrorHandler {
  static handle(error, context = "") {
    console.error(`API Error in ${context}:`, error);

    if (error.response) {
      // HTTP error response
      const { status, data } = error.response;

      switch (status) {
        case 400:
          return this.handleValidationError(data);
        case 401:
          return this.handleAuthError(data);
        case 403:
          return this.handlePermissionError(data);
        case 404:
          return this.handleNotFoundError(data);
        case 429:
          return this.handleRateLimitError(data);
        case 500:
          return this.handleServerError(data);
        default:
          return this.handleGenericError(data, status);
      }
    } else if (error.request) {
      // Network error
      return this.handleNetworkError();
    } else {
      // Other error
      return this.handleUnknownError(error);
    }
  }

  static handleValidationError(data) {
    const errors = [];

    if (typeof data === "object") {
      for (const [field, messages] of Object.entries(data)) {
        if (Array.isArray(messages)) {
          errors.push(`${field}: ${messages.join(", ")}`);
        } else {
          errors.push(`${field}: ${messages}`);
        }
      }
    }

    return {
      type: "validation",
      message: "Please check your input and try again",
      details: errors,
      userMessage: "Please correct the highlighted fields and try again.",
    };
  }

  static handleAuthError(data) {
    return {
      type: "authentication",
      message: "Authentication required",
      details: [data.detail || "Please log in to continue"],
      userMessage: "Please log in to continue.",
      action: "redirect_login",
    };
  }

  static handlePermissionError(data) {
    return {
      type: "permission",
      message: "Permission denied",
      details: [
        data.detail || "You do not have permission to perform this action",
      ],
      userMessage: "You do not have permission to perform this action.",
    };
  }

  static handleNotFoundError(data) {
    return {
      type: "not_found",
      message: "Resource not found",
      details: [data.detail || "The requested resource was not found"],
      userMessage: "The requested item could not be found.",
    };
  }

  static handleRateLimitError(data) {
    return {
      type: "rate_limit",
      message: "Rate limit exceeded",
      details: [data.detail || "Too many requests"],
      userMessage:
        "You are making requests too quickly. Please wait a moment and try again.",
      retryAfter: data.retry_after || 60,
    };
  }

  static handleServerError(data) {
    return {
      type: "server_error",
      message: "Server error",
      details: [data.detail || "An internal server error occurred"],
      userMessage: "Something went wrong on our end. Please try again later.",
    };
  }

  static handleNetworkError() {
    return {
      type: "network",
      message: "Network error",
      details: ["Could not connect to server"],
      userMessage:
        "Could not connect to the server. Please check your internet connection.",
    };
  }

  static handleGenericError(data, status) {
    return {
      type: "generic",
      message: `HTTP ${status} error`,
      details: [data.detail || `Request failed with status ${status}`],
      userMessage: "An unexpected error occurred. Please try again.",
    };
  }

  static handleUnknownError(error) {
    return {
      type: "unknown",
      message: "Unknown error",
      details: [error.message || "An unknown error occurred"],
      userMessage: "An unexpected error occurred. Please try again.",
    };
  }
}

// Usage with UI feedback
async function handleApiCall(
  apiCall,
  successMessage = "Operation completed successfully"
) {
  try {
    const result = await apiCall();
    showSuccessMessage(successMessage);
    return result;
  } catch (error) {
    const errorInfo = APIErrorHandler.handle(error, "API Call");
    showErrorMessage(errorInfo.userMessage);

    if (errorInfo.action === "redirect_login") {
      // Redirect to login page
      window.location.href = "/login";
    }

    throw errorInfo;
  }
}

// Example usage
async function createEventWithErrorHandling() {
  return handleApiCall(
    () =>
      eventManager.createEvent({
        title: "New Event",
        description: "Event description",
      }),
    "Event created successfully!"
  );
}

function showSuccessMessage(message) {
  // Implementation depends on your UI framework
  console.log("Success:", message);
}

function showErrorMessage(message) {
  // Implementation depends on your UI framework
  console.error("Error:", message);
}
```

## Complete Application Example

### React Component Integration

```jsx
import React, { useState, useEffect } from "react";

const GatherHubApp = () => {
  const [auth, setAuth] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize authentication
    const authInstance = new GatherHubAuth();
    setAuth(authInstance);

    // Check if user is already logged in
    if (authInstance.token) {
      loadEvents(authInstance);
    }
  }, []);

  const loadEvents = async (authInstance) => {
    setLoading(true);
    setError(null);

    try {
      const eventManager = new EventManager(authInstance);
      const eventsData = await eventManager.getEvents();
      setEvents(eventsData.results);
    } catch (err) {
      const errorInfo = APIErrorHandler.handle(err, "Loading Events");
      setError(errorInfo.userMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (email, password) => {
    try {
      await auth.login(email, password);
      await loadEvents(auth);
    } catch (err) {
      const errorInfo = APIErrorHandler.handle(err, "Login");
      setError(errorInfo.userMessage);
    }
  };

  const handleCreateEvent = async (eventData) => {
    try {
      const eventManager = new EventManager(auth);
      const newEvent = await eventManager.createEvent(eventData);
      setEvents((prev) => [newEvent, ...prev]);
    } catch (err) {
      const errorInfo = APIErrorHandler.handle(err, "Creating Event");
      setError(errorInfo.userMessage);
    }
  };

  if (!auth) {
    return <div>Loading...</div>;
  }

  if (!auth.token) {
    return <LoginForm onLogin={handleLogin} error={error} />;
  }

  return (
    <div className="gatherhub-app">
      <header>
        <h1>GatherHub</h1>
        <button onClick={() => auth.logout()}>Logout</button>
      </header>

      <main>
        {error && <div className="error">{error}</div>}

        <EventList
          events={events}
          loading={loading}
          onCreateEvent={handleCreateEvent}
          auth={auth}
        />
      </main>
    </div>
  );
};

export default GatherHubApp;
```

This comprehensive guide provides practical examples for integrating with all GatherHub API endpoints, including error handling, real-time features, and best practices for production applications.
