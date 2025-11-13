from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
import jwt

from .serializers import UserSerializer
from .models import User
from .serializers import FeedSerializer
from .models import Feed
from django.db.models import Count


class UserRegisterAPIView(APIView):
    """API for creating, reading, updating, and deleting user profiles"""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, pk=None):
     
        search_query = request.GET.get("search", None)

    
        if pk:
            try:
                user = User.objects.get(pk=pk)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

        elif search_query:
            users = User.objects.filter(
                Q(name__icontains=search_query) | Q(email__icontains=search_query)
            )
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.user.id != user.id:
            return Response(
                {"error": "You are not allowed to edit other users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User fully updated!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.user.id != user.id:
            return Response(
                {"error": "You are not allowed to edit other users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User partially updated!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(
                {"message": "User deleted successfully!"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

 
class UserLoginAPIView(APIView):
    """Manual login with JWT"""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=2),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        serializer = UserSerializer(user)
        return Response(
            {
                "message": "Login successful!",
                "token": token,
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class FeedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fast query — har feed ke sath likes_count ek hi query me
        feeds = Feed.objects.all().annotate(likes_count=Count("likes")).order_by("-created_at")
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != "teacher":
            return Response(
                {"error": "Only teachers can create feeds."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FeedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedLikeAPIView(APIView):
    """Students can like or unlike a feed."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Like or unlike feed"""
        try:
            feed = Feed.objects.get(pk=pk)
        except Feed.DoesNotExist:
            return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

  
        if user.role != "student":
            return Response({"error": "Only students can like feeds."}, status=status.HTTP_403_FORBIDDEN)

     
        if user in feed.likes.all():
            feed.likes.remove(user)
            message = "Feed unliked"
        else:
            feed.likes.add(user)
            message = "Feed liked"

        return Response({"message": message, "likes_count": feed.likes.count()}, status=status.HTTP_200_OK)
