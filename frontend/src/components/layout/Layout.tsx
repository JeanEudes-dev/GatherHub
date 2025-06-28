import React, { useEffect } from 'react'
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { Button } from '../ui/button'
import {
  initializeWebSockets,
  closeWebSockets,
} from '../../services/websocketService'
import { motion } from 'framer-motion'

const AuroraBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Simplified Aurora effect for now */}
      <div
        className="animate-aurora-1 absolute inset-0 transform-gpu [mask-image:radial-gradient(farthest-side_at_top_left,white,transparent)]"
        style={{
          background:
            'linear-gradient(to bottom right, #60a5fa, #a855f7, #ec4899)',
          opacity: 0.3,
        }}
      />
      <div
        className="animate-aurora-2 absolute inset-0 transform-gpu [mask-image:radial-gradient(farthest-side_at_bottom_right,white,transparent)]"
        style={{
          background: 'linear-gradient(to top left, #10b981, #f59e0b, #ef4444)',
          opacity: 0.2,
          animationDelay: '2s',
        }}
      />
      {/* Add more layers or more complex animations for a richer effect based on frontend/README.md */}
    </div>
  )
}


const Layout: React.FC = () => {
  const { isAuthenticated, user, logout, fetchProfile, accessToken } =
    useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (accessToken && !user) {
      fetchProfile().catch(error => {
        console.error('Failed to fetch profile on layout mount:', error)

        if (error.response?.status === 401) {
          logout()
        }
      })
    }
  }, [accessToken, user, fetchProfile, logout])

  useEffect(() => {
    if (isAuthenticated() && user) {
      console.log('Layout: User authenticated, initializing WebSockets.')
      initializeWebSockets()
    } else {
      console.log(
        'Layout: User not authenticated or user object missing, closing WebSockets.'
      )
      closeWebSockets()
    }

    return () => {
      console.log('Layout: Cleaning up WebSockets.')
      closeWebSockets()
    }
  }, [isAuthenticated, user])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="relative flex min-h-screen flex-col bg-transparent text-white">
      <AuroraBackground />
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <nav className="container flex h-14 max-w-screen-2xl items-center justify-between px-4 md:px-6">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <span className="text-lg font-bold sm:inline-block">
              {import.meta.env.VITE_APP_NAME || 'GatherHub'}
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              to="/events"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
            >
              Events
            </Link>
          </div>

          <div className="flex items-center gap-2">
            {isAuthenticated() && user ? (
              <>
                <span className="hidden text-sm text-muted-foreground sm:inline">
                  Welcome, {user.first_name || user.username}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/profile')}
                >
                  Profile
                </Button>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
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
        key={location.pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="container z-10 mx-auto max-w-screen-2xl flex-grow px-4 py-8 md:px-6"
      >
        <Outlet /> {/* Child routes will render here */}
      </motion.main>

      <footer className="z-10 border-t border-border/40 bg-background/95 py-6 backdrop-blur supports-[backdrop-filter]:bg-background/60 md:px-8 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-balance text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built by GatherHub Team. The source code is available on GitHub.{' '}
            {/* Placeholder */}
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
