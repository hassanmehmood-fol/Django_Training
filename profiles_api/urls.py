from django.urls import path
from .views import UserRegisterAPIView, UserLoginAPIView
from .views import FeedAPIView, FeedLikeAPIView


urlpatterns = [
    path("profile/", UserRegisterAPIView.as_view(), name="profile-method"),
    path("profile/<int:pk>/", UserRegisterAPIView.as_view(), name="profile-details"),
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("feeds/", FeedAPIView.as_view(), name="feeds"),
    path("feeds/<int:pk>/like/", FeedLikeAPIView.as_view(), name="feed-like"),
    
]
