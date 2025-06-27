import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
// import { toast } from 'sonner';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated, isLoading, error: authError } = useAuthStore();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/'); // Redirect if already logged in
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    setError(authError); // Sync with store error
  }, [authError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!username || !email || !password || !firstName || !lastName) {
      setError('All fields are required.');
      return;
    }

    const user = await register({
      username,
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });

    if (user) {
      // toast.success('Registration successful! Welcome!');
      navigate('/'); // Navigate to dashboard or home
    } else {
      // setError(authError || 'Registration failed. Please try again.');
      // toast.error(authError || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-10rem)] py-12">
      <Card className="w-full max-w-lg glass-card"> {/* Apply glass-card style */}
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-white">Create your Account</CardTitle>
          <CardDescription className="text-gray-300">
            Join GatherHub and start planning your community events today!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="firstName" className="text-gray-200">First Name</Label>
                <Input id="firstName" placeholder="John" value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="lastName" className="text-gray-200">Last Name</Label>
                <Input id="lastName" placeholder="Doe" value={lastName} onChange={(e) => setLastName(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="username" className="text-gray-200">Username</Label>
              <Input id="username" placeholder="johndoe" value={username} onChange={(e) => setUsername(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-gray-200">Email</Label>
              <Input id="email" type="email" placeholder="m@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-gray-200">Password</Label>
              <Input id="password" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirmPassword" className="text-gray-200">Confirm Password</Label>
              <Input id="confirmPassword" type="password" placeholder="••••••••" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-400 text-white"/>
            </div>
            {error && <p className="text-sm text-red-400 text-center">{error}</p>}
            <Button type="submit" className="w-full btn-aurora" disabled={isLoading}>
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="text-center block">
          <p className="text-sm text-gray-300">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-aurora-purple hover:underline">
              Log in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};

export default RegisterPage;
