from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary="User Registration",
        description="Register a new user with email and password. Returns user data and JWT tokens.",
        tags=["Authentication"]
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
                    'id': user.pk,
                    'email': user.email,
                    'name': user.name,
                },
                'tokens': serializer.get_tokens(user),
                'message': 'User registered successfully.'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Get User Profile",
        description="Get current authenticated user's profile information.",
        tags=["User Profile"]
    ),
    put=extend_schema(
        summary="Update User Profile",
        description="Update current authenticated user's profile (name and avatar).",
        tags=["User Profile"]
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
        description="Delete current authenticated user's avatar.",
        tags=["User Profile"]
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
        description="Change current authenticated user's password.",
        tags=["Authentication"]
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
