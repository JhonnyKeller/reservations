from django.urls import path
from base.views import users_views as views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('profile/', views.getUserProfile, name="user-profile"),
    path('profile/update/', views.updateUserProfile, name="user-update"),
    path('', views.getUsers, name="users"),
    path('login/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', views.registerUser, name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]