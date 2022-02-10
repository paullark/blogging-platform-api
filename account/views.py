# from .forms import RegisterForm, ProfileEditForm
# from .services.subscription_service import \
#     subscribe_user, \
#     get_user_subscriptions
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


from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserDetailSerializer
from rest_framework.permissions import IsAuthenticated


class UserListView(APIView):
    """
        View для вывода фильтрованного и сортированного списка пользователей.
        Доступен только для авторизованных пользователей.
        Для пагинации используется миксин
    """
    def get(self, request):
        filter_by = request.GET.get('filter_by')
        order_by = request.GET.get('order_by')
        username = request.GET.get('username')

        users = get_filtered_and_sorted_user_list(username or request.user.username,
                                                  filter_by, order_by)

        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)


class ProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer
    lookup_field = 'username'


