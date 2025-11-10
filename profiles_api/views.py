from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User

class UserRegisterAPIView(APIView):
    """API for creating and fetching user profiles"""


    def get(self, request):
        users = User.objects.all()  
        serializer = UserSerializer(users, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)

  
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
