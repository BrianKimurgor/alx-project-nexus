from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user with email, username, and password.",
        request=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(generics.GenericAPIView):
    """User login view"""
    serializer_class = UserSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticates a user and returns an access and refresh token.",
        request=UserSerializer,
        responses={200: {"type": "object", "properties": {
            "refresh": {"type": "string"},
            "access": {"type": "string"}
        }}}
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.filter(username=username).first()


        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """User logout view"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="User Logout",
        description="Logs out a user by blacklisting the refresh token.",
        request={"type": "object", "properties": {"refresh_token": {"type": "string"}}},
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token to prevent reuse

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve and update user profile"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve the logged-in user's profile."""
        return self.request.user

    @extend_schema(
        summary="Get User Profile",
        description="Retrieve details of the currently logged-in user.",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Return user profile details."""
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update User Profile",
        description="Update user details such as username, first name, and last name.",
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request, *args, **kwargs):
        """Update user profile details."""
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
