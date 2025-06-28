from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse
from drf_spectacular.openapi import AutoSchema
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary="User Registration",
        description="""
        Register a new user with email and password. 
        
        This endpoint creates a new user account and returns JWT tokens for immediate authentication.
        
        **Rate Limit**: 5 requests per minute per IP address.
        
        **Validation Rules**:
        - Email must be unique and valid format
        - Password must be at least 8 characters
        - Name is required and must be between 2-50 characters
        """,
        tags=["Authentication"],
        examples=[
            OpenApiExample(
                'Valid Registration',
                summary='Successful user registration',
                description='Example of a valid registration request',
                value={
                    'email': 'john.doe@example.com',
                    'password': 'securepassword123',
                    'name': 'John Doe'
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=UserRegistrationSerializer,
                description='User successfully registered',
                examples=[
                    OpenApiExample(
                        'Registration Success',
                        summary='Successful registration response',
                        description='User created with JWT tokens',
                        value={
                            'user': {
                                'id': 1,
                                'email': 'john.doe@example.com',
                                'name': 'John Doe'
                            },
                            'tokens': {
                                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                            },
                            'message': 'User registered successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid input data',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        summary='Invalid registration data',
                        description='Example validation error response',
                        value={
                            'email': ['This field is required.'],
                            'password': ['This password is too short. It must contain at least 8 characters.']
                        }
                    )
                ]
            ),
            429: OpenApiResponse(
                description='Rate limit exceeded',
                examples=[
                    OpenApiExample(
                        'Rate Limit',
                        summary='Too many registration attempts',
                        description='Rate limit exceeded response',
                        value={
                            'error': 'Rate limit exceeded',
                            'detail': 'Too many requests. Please try again later.',
                            'type': 'auth'
                        }
                    )
                ]
            )
        }
    )
)
class UserRegistrationView(APIView):
    """
    User registration endpoint with email validation and JWT token generation.
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        """
        Register a new user.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Return user data with tokens
            response_data = {
                'user': {
                    'id': user.pk, # type: ignore
                    'email': user.email, # type: ignore
                    'first_name': user.first_name, # type: ignore
                    'last_name': user.last_name, # type: ignore
                },
                'tokens': serializer.get_tokens(user), # type: ignore
                'message': 'User registered successfully.'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Get User Profile",
        description="""
        Retrieve the current authenticated user's profile information.
        
        Returns detailed user profile including avatar URL if available.
        
        **Authentication Required**: Bearer token in Authorization header.
        """,
        tags=["User Profile"],
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer,
                description='User profile retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Profile Response',
                        summary='User profile data',
                        description='Complete user profile information',
                        value={
                            'id': 1,
                            'email': 'john.doe@example.com',
                            'name': 'John Doe',
                            'avatar': 'http://localhost:8000/media/avatars/john_doe.jpg',
                            'date_joined': '2023-12-01T10:30:00Z',
                            'is_active': True
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Authentication required',
                examples=[
                    OpenApiExample(
                        'Unauthorized',
                        summary='Missing or invalid token',
                        description='Authentication credentials not provided',
                        value={
                            'detail': 'Authentication credentials were not provided.'
                        }
                    )
                ]
            )
        }
    ),
    put=extend_schema(
        summary="Update User Profile",
        description="""
        Update the current authenticated user's profile information.
        
        Supports partial updates - only provided fields will be updated.
        
        **Updatable Fields**:
        - name: User's display name (2-50 characters)
        - avatar: Profile image file (max 5MB, JPEG/PNG)
        
        **Authentication Required**: Bearer token in Authorization header.
        """,
        tags=["User Profile"],
        examples=[
            OpenApiExample(
                'Profile Update',
                summary='Update user name',
                description='Example of updating user profile',
                value={
                    'name': 'John Smith'
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer,
                description='Profile updated successfully',
                examples=[
                    OpenApiExample(
                        'Update Success',
                        summary='Profile updated response',
                        description='Updated profile data',
                        value={
                            'user': {
                                'id': 1,
                                'email': 'john.doe@example.com',
                                'name': 'John Smith',
                                'avatar': 'http://localhost:8000/media/avatars/john_smith.jpg',
                                'date_joined': '2023-12-01T10:30:00Z',
                                'is_active': True
                            },
                            'message': 'Profile updated successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid input data',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        summary='Invalid profile data',
                        description='Profile validation error',
                        value={
                            'name': ['This field may not be blank.']
                        }
                    )
                ]
            )
        }
    )
)
class UserProfileView(APIView):
    """
    View for managing user profiles. Users can only access/modify their own profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get current user's profile.
        """
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update current user's profile.
        """
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Return updated profile data
            profile_serializer = UserProfileSerializer(
                request.user,
                context={'request': request}
            )
            
            response_data = {
                'user': profile_serializer.data,
                'message': 'Profile updated successfully.'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    delete=extend_schema(
        summary="Delete User Avatar",
        description="""
        Remove the current authenticated user's profile avatar.
        
        This will delete the avatar file from storage and reset the user's avatar field.
        
        **Authentication Required**: Bearer token in Authorization header.
        """,
        tags=["User Profile"],
        responses={
            200: OpenApiResponse(
                description='Avatar deleted successfully',
                examples=[
                    OpenApiExample(
                        'Delete Success',
                        summary='Avatar removal confirmation',
                        description='Avatar successfully deleted',
                        value={
                            'message': 'Avatar deleted successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='No avatar to delete',
                examples=[
                    OpenApiExample(
                        'No Avatar',
                        summary='User has no avatar',
                        description='No avatar file to delete',
                        value={
                            'message': 'No avatar to delete.'
                        }
                    )
                ]
            )
        }
    )
)
class UserAvatarView(APIView):
    """
    View for managing user avatar.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """
        Delete user's avatar.
        """
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
            
            return Response({
                'message': 'Avatar deleted successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'No avatar to delete.'
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="Change Password",
        description="""
        Change the current authenticated user's password.
        
        Requires the current password for verification and a new password that meets security requirements.
        
        **Security Requirements**:
        - Current password must be provided and correct
        - New password must be at least 8 characters
        - New password cannot be the same as current password
        
        **Authentication Required**: Bearer token in Authorization header.
        **Rate Limit**: 5 requests per minute per user.
        """,
        tags=["Authentication"],
        examples=[
            OpenApiExample(
                'Password Change',
                summary='Change user password',
                description='Example password change request',
                value={
                    'current_password': 'oldpassword123',
                    'new_password': 'newpassword456'
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Password changed successfully',
                examples=[
                    OpenApiExample(
                        'Change Success',
                        summary='Password change confirmation',
                        description='Password successfully updated',
                        value={
                            'message': 'Password changed successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid password data',
                examples=[
                    OpenApiExample(
                        'Invalid Password',
                        summary='Password validation error',
                        description='Current password incorrect or new password invalid',
                        value={
                            'current_password': ['Current password is incorrect.'],
                            'new_password': ['This password is too short. It must contain at least 8 characters.']
                        }
                    )
                ]
            )
        }
    )
)
class PasswordChangeView(APIView):
    """
    View for changing user password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        """
        Change user's password.
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'message': 'Password changed successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="User Login",
        description="""
        Authenticate a user and return JWT tokens.

        Accepts email and password, validates credentials, and returns access/refresh tokens and user info.
        """,
        tags=["Authentication"],
        examples=[
            OpenApiExample(
                'Valid Login',
                summary='Successful user login',
                description='Example of a valid login request',
                value={
                    'email': 'john.doe@example.com',
                    'password': 'securepassword123'
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Login successful',
                examples=[
                    OpenApiExample(
                        'Login Success',
                        summary='Successful login response',
                        description='User authenticated with JWT tokens',
                        value={
                            'user': {
                                'id': 1,
                                'email': 'john.doe@example.com',
                                'name': 'John Doe'
                            },
                            'tokens': {
                                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                            },
                            'message': 'Login successful.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid credentials',
                examples=[
                    OpenApiExample(
                        'Login Error',
                        summary='Invalid login data',
                        description='Invalid email or password',
                        value={
                            'detail': 'Invalid credentials.'
                        }
                    )
                ]
            )
        }
    )
)
class UserLoginView(APIView):
    """
    User login endpoint with JWT token generation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email :
            return Response(
                {'detail': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not password:
            return Response(
                {'detail': 'Password is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'No user found with this email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response(
                {'detail': 'Incorrect password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        response_data = {
            'user': {
                'id': user.pk,
                'email': user.email,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'Login successful.'
        }
        return Response(response_data, status=status.HTTP_200_OK)
