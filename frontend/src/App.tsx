import React, { useEffect } from 'react'
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet,
  Link,
} from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import EventListPage from './pages/EventListPage'
import CreateEventPage from './pages/CreateEventPage'
import EditEventPage from './pages/EditEventPage'
import EventDetailPage from './pages/EventDetailPage'
import { useAuthStore, rehydrateAuth } from './store/authStore'
import { Toaster } from 'react-hot-toast'

const ProtectedRoute: React.FC = () => {
  const { isLoading } = useAuthStore.getState()
  const token = localStorage.getItem('access')

  if (isLoading) {
    return <div>Loading authentication status...</div>
  }

  const authStatus = useAuthStore.getState().isAuthenticated()

  if (!authStatus && !token) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

function App() {
  useEffect(() => {
    rehydrateAuth()
    const { accessToken, user, fetchProfile, logout } = useAuthStore.getState()
    if (accessToken && !user) {
      fetchProfile().catch(err => {
        console.error('App.tsx: Initial profile fetch failed', err)

        if (err.response?.status === 401) {
          logout()
        }
      })
    }
  }, [])

  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        <Route element={<Layout />}>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/events/new" element={<CreateEventPage />} />
            <Route path="/events/edit/:eventId" element={<EditEventPage />} />
            {/* Add other protected routes here for tasks, voting specific actions if needed */}
          </Route>

          <Route path="/events" element={<EventListPage />} />

          <Route path="/events/:eventId" element={<EventDetailPage />} />

          {/* Catch-all for 404 Not Found (Optional) */}
          <Route
            path="*"
            element={
              <div>
                <h2>404 Not Found</h2>
                <Link to="/">Go Home</Link>
              </div>
            }
          />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
