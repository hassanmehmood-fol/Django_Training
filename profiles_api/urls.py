from django.urls import path
from .views import UserRegisterAPIView, UserLoginAPIView

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('register/<int:pk>/', UserRegisterAPIView.as_view(), name='user-detail'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
]
