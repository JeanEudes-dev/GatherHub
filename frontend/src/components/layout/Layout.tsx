import React, { ReactNode, useEffect } from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/button'; // Assuming shadcn/ui button
import { initializeWebSockets, closeWebSockets } from '../../services/websocketService';
import { motion } from 'framer-motion';

// Placeholder for AuroraBackground component - to be created later
const AuroraBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Simplified Aurora effect for now */}
      <div
        className="absolute inset-0 transform-gpu animate-aurora-1 [mask-image:radial-gradient(farthest-side_at_top_left,white,transparent)]"
        style={{
          background: 'linear-gradient(to bottom right, #60a5fa, #a855f7, #ec4899)',
          opacity: 0.3,
        }}
      />
      <div
        className="absolute inset-0 transform-gpu animate-aurora-2 [mask-image:radial-gradient(farthest-side_at_bottom_right,white,transparent)]"
        style={{
          background: 'linear-gradient(to top left, #10b981, #f59e0b, #ef4444)',
          opacity: 0.2,
          animationDelay: '2s',
        }}
      />
       {/* Add more layers or more complex animations for a richer effect based on frontend/README.md */}
    </div>
  );
};

// Add animation keyframes to src/index.css or src/styles/globals.css
/*
@keyframes aurora-1 {
  0%, 100% { transform: translateX(0) translateY(0) scale(1); }
  50% { transform: translateX(20px) translateY(10px) scale(1.1); }
}
@keyframes aurora-2 {
  0%, 100% { transform: translateX(0) translateY(0) scale(1); }
  50% { transform: translateX(-15px) translateY(-5px) scale(1.05); }
}
.animate-aurora-1 { animation: aurora-1 15s infinite ease-in-out; }
.animate-aurora-2 { animation: aurora-2 18s infinite ease-in-out; }
*/


const Layout: React.FC = () => {
  const { isAuthenticated, user, logout, fetchProfile, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation(); // Get location for AnimatePresence key or motion key

  useEffect(() => {
    // If there's a token but no user data, fetch profile (e.g., after page refresh and rehydration)
    if (accessToken && !user) {
      fetchProfile().catch(error => {
        console.error("Failed to fetch profile on layout mount:", error);
        // If profile fetch fails (e.g. token expired), logout
        if (error.response?.status === 401) {
          logout(); // This will also trigger WS close via the other useEffect
        }
      });
    }
  }, [accessToken, user, fetchProfile, logout]);

  useEffect(() => {
    // Manage WebSocket connection based on authentication state
    if (isAuthenticated() && user) { // Ensure user object is also present
      console.log("Layout: User authenticated, initializing WebSockets.");
      initializeWebSockets();
    } else {
      console.log("Layout: User not authenticated or user object missing, closing WebSockets.");
      closeWebSockets();
    }

    // Cleanup function for when the Layout component unmounts or auth state changes to non-authed
    return () => {
      console.log("Layout: Cleaning up WebSockets.");
      closeWebSockets();
    };
  }, [isAuthenticated, user]); // Depend on user object as well to ensure it's loaded

  const handleLogout = async () => {
    // closeWebSockets() will be called by the useEffect above when isAuthenticated becomes false
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-transparent text-white relative">
      <AuroraBackground />
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <nav className="container flex h-14 max-w-screen-2xl items-center justify-between px-4 md:px-6">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold sm:inline-block text-lg">
              {import.meta.env.VITE_APP_NAME || 'GatherHub'}
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link to="/events" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">Events</Link>
          </div>

          <div className="flex items-center gap-2">
            {isAuthenticated() && user ? (
              <>
                <span className="text-sm text-muted-foreground hidden sm:inline">Welcome, {user.first_name || user.username}</span>
                <Button variant="outline" size="sm" onClick={() => navigate('/profile')}>Profile</Button>
                <Button variant="ghost" size="sm" onClick={handleLogout}>Logout</Button>
              </>
            ) : (
              <>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/login">Login</Link>
                </Button>
                <Button variant="default" size="sm" asChild>
                  <Link to="/register">Sign Up</Link>
                </Button>
              </>
            )}
          </div>
        </nav>
      </header>

      <motion.main
        key={location.pathname} // Trigger animation on route change
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="flex-grow container max-w-screen-2xl mx-auto px-4 py-8 md:px-6 z-10"
      >
        <Outlet /> {/* Child routes will render here */}
      </motion.main>

      <footer className="py-6 md:px-8 md:py-0 border-t border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-10">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-balance text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built by GatherHub Team. The source code is available on GitHub. {/* Placeholder */}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
