import React from 'react';
import { useAuthStore } from '../store/authStore';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';

const HomePage: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore();

  return (
    <div className="container mx-auto py-8 text-center">
      <h1 className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-aurora-blue via-aurora-purple to-aurora-pink">
        Welcome to GatherHub!
      </h1>
      {isAuthenticated() && user ? (
        <div>
          <p className="text-xl text-gray-300 mb-4">
            Hello, {user.first_name || user.username}! Ready to plan or join some events?
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
          <p className="text-xl text-gray-300 mb-8">
            Your central place to organize, manage, and participate in community events.
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
        <h2 className="text-3xl font-semibold mb-6 text-white">Featured Events</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Example Event Card Placeholders */}
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card p-6 rounded-lg">
              <h3 className="text-xl font-bold text-white mb-2">Event Title {i}</h3>
              <p className="text-gray-400 mb-1 text-sm">Date: 2025-XX-XX</p>
              <p className="text-gray-400 mb-3 text-sm">Location: Community Hall</p>
              <p className="text-gray-300 text-sm mb-4">A brief description of the upcoming event. Join us for fun and collaboration!</p>
              <Button variant="ghost" className="w-full text-aurora-blue hover:bg-aurora-blue/10">View Details</Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
