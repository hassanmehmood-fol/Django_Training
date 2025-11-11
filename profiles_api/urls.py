from django.urls import path
from .views import UserRegisterAPIView, UserLoginAPIView

urlpatterns = [
    path('profile/', UserRegisterAPIView.as_view(), name='profile-method'),
    path('profile/<int:pk>/', UserRegisterAPIView.as_view(), name='profile-details'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
]
