import React from 'react'
import { useAuthStore } from '../store/authStore'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'

const HomePage: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore()

  return (
    <div className="container mx-auto py-8 text-center">
      <h1 className="mb-6 bg-gradient-to-r from-aurora-blue via-aurora-purple to-aurora-pink bg-clip-text text-5xl font-bold text-transparent">
        Welcome to GatherHub!
      </h1>
      {isAuthenticated() && user ? (
        <div>
          <p className="mb-4 text-xl text-gray-300">
            Hello, {user.first_name || user.username}! Ready to plan or join
            some events?
          </p>
          <div className="space-x-4">
            <Button asChild className="btn-aurora">
              <Link to="/events">Browse Events</Link>
            </Button>
            <Button asChild variant="outline" className="btn-glass">
              <Link to="/events/new">Create New Event</Link>
            </Button>
          </div>
        </div>
      ) : (
        <div>
          <p className="mb-8 text-xl text-gray-300">
            Your central place to organize, manage, and participate in community
            events.
            <br />
            Log in or sign up to get started!
          </p>
          <div className="space-x-4">
            <Button asChild size="lg" className="btn-aurora">
              <Link to="/login">Login</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="btn-glass">
              <Link to="/register">Sign Up</Link>
            </Button>
          </div>
        </div>
      )}

      {/* Placeholder for featured events or other content */}
      <div className="mt-16">
        <h2 className="mb-6 text-3xl font-semibold text-white">
          Featured Events
        </h2>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Example Event Card Placeholders */}
          {[1, 2, 3].map(i => (
            <div key={i} className="glass-card rounded-lg p-6">
              <h3 className="mb-2 text-xl font-bold text-white">
                Event Title {i}
              </h3>
              <p className="mb-1 text-sm text-gray-400">Date: 2025-XX-XX</p>
              <p className="mb-3 text-sm text-gray-400">
                Location: Community Hall
              </p>
              <p className="mb-4 text-sm text-gray-300">
                A brief description of the upcoming event. Join us for fun and
                collaboration!
              </p>
              <Button
                variant="ghost"
                className="w-full text-aurora-blue hover:bg-aurora-blue/10"
              >
                View Details
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default HomePage
