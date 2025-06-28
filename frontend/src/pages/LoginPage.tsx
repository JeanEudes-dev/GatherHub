import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
// import { toast } from 'sonner'; // Or your preferred toast library

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, isAuthenticated, isLoading, error: authError } = useAuthStore()
  const [usernameOrEmail, setUsernameOrEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/') // Redirect to home or dashboard if already logged in
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    setError(authError) // Sync local error state with store error
  }, [authError])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null) // Clear previous errors
    if (!usernameOrEmail || !password) {
      setError('Both username/email and password are required.')
      return
    }

    const user = await login({ email: usernameOrEmail, password })

    if (user) {
      // toast.success('Login successful!'); // Example toast
      navigate('/')
    } else {
      // Error is handled by the store and updated via useEffect
      // setError(authError || 'Login failed. Please check your credentials.');
      // toast.error(authError || 'Login failed. Please check your credentials.');
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-10rem)] items-center justify-center py-12">
      <Card className="glass-card w-full max-w-md">
        {' '}
        {/* Apply glass-card style */}
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-white">
            Welcome Back!
          </CardTitle>
          <CardDescription className="text-gray-300">
            Enter your credentials to access your GatherHub account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="usernameOrEmail" className="text-gray-200">
                Username or Email
              </Label>
              <Input
                id="usernameOrEmail"
                type="text"
                placeholder="yourname or user@example.com"
                value={usernameOrEmail}
                onChange={e => setUsernameOrEmail(e.target.value)}
                required
                className="border-white/20 bg-white/10 text-white placeholder-gray-400"
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-gray-200">
                  Password
                </Label>
                <Link
                  to="/forgot-password" // Placeholder for forgot password functionality
                  className="text-sm text-aurora-blue hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="border-white/20 bg-white/10 text-white placeholder-gray-400"
              />
            </div>
            {error && (
              <p className="text-center text-sm text-red-400">{error}</p>
            )}
            <Button
              type="submit"
              className="btn-aurora w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="block text-center">
          <p className="text-sm text-gray-300">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-medium text-aurora-purple hover:underline"
            >
              Sign up
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  )
}

export default LoginPage
