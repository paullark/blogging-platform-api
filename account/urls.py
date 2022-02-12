from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('auth/registration/',
         views.UserRegistrationView.as_view(),
         name='user_registration'),
    path('auth/token/login/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),

    path('password-reset/email/',
         views.PasswordResetEmailView.as_view(),
         name='password_reset_email'),
    path('password-reset/<str:uidb64>/<str:token>/',
         views.PasswordResetConfirm.as_view(),
         name='password_reset_confirm'),

    path('profile/edit/',
         views.ProfileEditView.as_view(),
         name='profile_edit'),
    path('profile/edit/change-password/',
         views.PasswordChangeView.as_view(),
         name='password_change'),
    path('profile/<str:username>/',
         views.ProfileView.as_view(),
         name='profile'),

    path('user-list/',
         views.UserListView.as_view(),
         name='user_list'),

    path('subscribe/', views.SubscriptionUserView.as_view(),
         name='subscribe_to_user'),
]
