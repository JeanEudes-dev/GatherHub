import React, { useEffect, useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import { toast } from 'react-hot-toast'
interface UpdateProfileData {
  first_name?: string
  last_name?: string
  bio?: string
  avatar?: File | string | null
}
const ProfilePage: React.FC = () => {
  const {
    user,
    fetchProfile,
    updateProfile,
    isLoading,
    error: authError,
  } = useAuthStore()

  const [isEditing, setIsEditing] = useState(false)
  const [firstName, setFirstName] = useState(user?.first_name || '')
  const [lastName, setLastName] = useState(user?.last_name || '')
  const [bio, setBio] = useState(user?.bio || '')
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(
    user?.avatar || null
  )
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) {
      fetchProfile()
    } else {
      setFirstName(user.first_name || '')
      setLastName(user.last_name || '')
      setBio(user.bio || '')
      setAvatarPreview(user.avatar || null)
    }
  }, [user, fetchProfile])

  useEffect(() => {
    setError(authError)
  }, [authError])

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0]
      setAvatarFile(file)
      setAvatarPreview(URL.createObjectURL(file))
    }
  }

  const handleSaveChanges = async () => {
    setError(null)
    const profileData: UpdateProfileData = {
      first_name: firstName,
      last_name: lastName,
      bio: bio,
      avatar: avatarFile,
    }

    // The API Reference suggests `avatar` is a file.
    // The authService `updateUserProfile` expects profileData to be FormData if avatar is a File.

    let dataToSend: FormData | Parameters<typeof updateProfile>[0] = profileData

    if (avatarFile) {
      const formData = new FormData()
      formData.append('first_name', firstName)
      formData.append('last_name', lastName)
      formData.append('bio', bio)
      formData.append('avatar', avatarFile)
      dataToSend = formData
    }

    const updatedUser = await updateProfile(dataToSend)
    if (updatedUser) {
      toast.success('Profile updated successfully!')
      setIsEditing(false)
    } else {
      toast.error(error || 'Failed to update profile.')
    }
  }

  if (isLoading && !user && !isEditing) {
    // Show loading only on initial fetch
    return <div className="py-10 text-center">Loading profile...</div>
  }

  if (!user) {
    return (
      <div className="py-10 text-center text-red-400">
        {error || 'Could not load profile. Please try logging in again.'}
      </div>
    )
  }

  const userInitial = user.first_name
    ? user.first_name.charAt(0).toUpperCase()
    : user.username.charAt(0).toUpperCase()

  return (
    <div className="container mx-auto py-8">
      <Card className="glass-card mx-auto w-full max-w-2xl">
        <CardHeader>
          <div className="flex flex-col items-center gap-6 sm:flex-row">
            <div className="relative">
              <Avatar className="h-24 w-24 border-2 border-aurora-purple text-3xl">
                <AvatarImage
                  src={avatarPreview || undefined}
                  alt={user.username}
                />
                <AvatarFallback>{userInitial}</AvatarFallback>
              </Avatar>
              {isEditing && (
                <div className="absolute bottom-0 right-0">
                  <Input
                    type="file"
                    id="avatarUpload"
                    className="hidden"
                    onChange={handleAvatarChange}
                    accept="image/*"
                  />
                  <Label
                    htmlFor="avatarUpload"
                    className="cursor-pointer rounded-full bg-aurora-blue p-1.5 text-xs text-white shadow-md hover:bg-aurora-pink"
                    title="Change avatar"
                  >
                    {/* Placeholder for an edit icon */}
                    ✏️
                  </Label>
                </div>
              )}
            </div>
            <div>
              <CardTitle className="text-3xl font-bold text-white">
                {user.username}
              </CardTitle>
              <CardDescription className="text-gray-300">
                {user.email}
              </CardDescription>
              <p className="mt-1 text-sm text-gray-400">
                Joined:{' '}
                {new Date(user.date_joined || Date.now()).toLocaleDateString()}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && <p className="text-center text-sm text-red-400">{error}</p>}
          {isEditing ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="firstName" className="text-gray-200">
                  First Name
                </Label>
                <Input
                  id="firstName"
                  value={firstName}
                  onChange={e => setFirstName(e.target.value)}
                  className="border-white/20 bg-white/10 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName" className="text-gray-200">
                  Last Name
                </Label>
                <Input
                  id="lastName"
                  value={lastName}
                  onChange={e => setLastName(e.target.value)}
                  className="border-white/20 bg-white/10 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio" className="text-gray-200">
                  Bio
                </Label>
                <textarea
                  id="bio"
                  value={bio}
                  onChange={e => setBio(e.target.value)}
                  rows={3}
                  className="w-full rounded-md border-white/20 bg-white/10 p-2 text-white placeholder-gray-400"
                  placeholder="Tell us a bit about yourself..."
                />
              </div>
              <div className="flex gap-4">
                <Button
                  onClick={handleSaveChanges}
                  className="btn-aurora"
                  disabled={isLoading}
                >
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button
                  variant="outline"
                  className="btn-glass"
                  onClick={() => {
                    setIsEditing(false)
                    setError(null) /* Reset form if needed */
                  }}
                >
                  Cancel
                </Button>
              </div>
            </>
          ) : (
            <>
              <div>
                <h3 className="text-sm font-medium text-gray-400">Full Name</h3>
                <p className="text-lg text-white">
                  {user.first_name || ''} {user.last_name || ''}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-400">Bio</h3>
                <p className="whitespace-pre-wrap text-lg text-white">
                  {user.bio || (
                    <span className="italic text-gray-500">No bio yet.</span>
                  )}
                </p>
              </div>
              <Button
                onClick={() => setIsEditing(true)}
                className="btn-aurora w-full sm:w-auto"
              >
                Edit Profile
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ProfilePage
