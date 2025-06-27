import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import EventListPage from './pages/EventListPage';
import CreateEventPage from './pages/CreateEventPage';
import EditEventPage from './pages/EditEventPage';
import EventDetailPage from './pages/EventDetailPage';
import { useAuthStore, rehydrateAuth } from './store/authStore';
// import { Toaster } from 'sonner'; // If using sonner for toasts

// A wrapper for protected routes
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuthStore.getState(); // Direct state access for guard
  const token = localStorage.getItem('accessToken'); // Check token directly as store might not be hydrated yet

  // Give a moment for store rehydration if it's happening
  if (isLoading) {
    return <div>Loading authentication status...</div>; // Or a spinner
  }

  // Use isAuthenticated from the store if available, otherwise fallback to token check
  const authStatus = useAuthStore.getState().isAuthenticated();


  if (!authStatus && !token) { // If not authenticated and no token at all
    return <Navigate to="/login" replace />;
  }

  // If there's a token but user isn't in store yet (e.g. after refresh), Layout will try to fetchProfile.
  // Outlet allows rendering child routes.
  return <Outlet />;
};


function App() {
  // Attempt to rehydrate auth state on initial load
  // This helps if Zustand's persist middleware hasn't finished by the first render.
  useEffect(() => {
    rehydrateAuth(); // Ensure tokens from localStorage are loaded into Zustand state
    const { accessToken, user, fetchProfile, logout } = useAuthStore.getState();
    if (accessToken && !user) {
      fetchProfile().catch(err => {
        console.error("App.tsx: Initial profile fetch failed", err);
        // Potentially logout if token is invalid
        if (err.response?.status === 401) {
            logout();
        }
      });
    }
  }, []);

  return (
    <Router>
      {/* <Toaster position="top-right" richColors /> */}
      <Routes>
        <Route element={<Layout />}>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Placeholder for other public pages like 'About', 'Contact', etc. */}
          {/* <Route path="/about" element={<AboutPage />} /> */}

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/events/new" element={<CreateEventPage />} />
            <Route path="/events/edit/:eventId" element={<EditEventPage />} />
            {/* Add other protected routes here for tasks, voting specific actions if needed */}
          </Route>

          {/* Event routes that can be public or protected based on content */}
          {/* Listing events is often public */}
          <Route path="/events" element={<EventListPage />} />
          {/* Event detail can be public, actions within might be protected by component logic */}
          <Route path="/events/:eventId" element={<EventDetailPage />} />

          {/* Catch-all for 404 Not Found (Optional) */}
          <Route path="*" element={<div><h2>404 Not Found</h2><Link to="/">Go Home</Link></div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
