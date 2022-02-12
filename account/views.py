# from .forms import RegisterForm, ProfileEditForm
from .services.subscription_service import subscribe_user
from .services.users_range_service import \
    get_filtered_and_sorted_user_list,\
    get_user_object
# from .services.rating_service import UsersRating
# from blog.services.view_mixins import PaginatorMixin
# from django.conf import settings
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.http import HttpRequest, HttpResponse, JsonResponse
# from django.shortcuts import render, redirect
# from django.views.generic.base import View


from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import (
    UserListSerializer, UserDetailSerializer, UserCreateUpdateSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserCreateUpdateSerializer


class ProfileEditView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserCreateUpdateSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = self.serializer_class(instance=request.user,
                                           data=request.data,
                                           partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filter_by = self.request.query_params.get('filter_by')
        order_by = self.request.query_params.get('order_by')
        username = self.request.query_params.get('username')

        users = get_filtered_and_sorted_user_list(username or self.request.user.username,
                                                  filter_by, order_by)
        return users


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return get_user_object(self.kwargs[self.lookup_field])


class SubscriptionUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        action = request.data.get('action')
        if username and action:
            if subscribe_user(from_user=request.user,
                              to_user_username=username,
                              action=action):
                return Response(status=201)
        return Response(status=400)
