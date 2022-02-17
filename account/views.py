from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    UserListSerializer, UserDetailUpdateSerializer, UserCreateSerializer,
    PasswordChangeSerializer, PasswordSetSerializer
)
from .services.auth_service import (
    send_confirm_password_reset_email, check_confirm_reset_data
)
from .services.subscription_service import subscribe_user
from .services.users_range_service import (
    get_filtered_and_sorted_user_list,
    get_user_object
)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя"""
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer


class UserListView(generics.ListAPIView):
    """Отображение списка пользователей"""
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        filter_by = self.request.query_params.get('filter')
        order_by = self.request.query_params.get('order')
        username = self.request.query_params.get('username')

        users = get_filtered_and_sorted_user_list(username or self.request.user.username,
                                                  filter_by, order_by)
        return users


class ProfileDetailUpdateView(generics.RetrieveUpdateAPIView):
    """Отображение и изменение информации о пользователе"""
    serializer_class = UserDetailUpdateSerializer
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, IsProfileOwnerOrReadOnly)

    def get_object(self, queryset=None):
        user = get_user_object(self.kwargs[self.lookup_field])
        self.check_object_permissions(self.request, user)
        return user


class PasswordChangeView(generics.UpdateAPIView):
    """Изменение пароля"""
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user,
                                           data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class PasswordResetEmailView(APIView):
    """Отправка email с подтверждением сброса пароля"""
    permission_classes = (AllowAny,)

    def post(self, request):
        if send_confirm_password_reset_email(request):
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirm(APIView):
    """Изменение пароля после подтверждения по email"""
    permission_classes = (AllowAny,)
    serializer_class = PasswordSetSerializer

    def patch(self, request, uidb64, token):
        if check_confirm_reset_data(uidb64, token):
            serializer = self.serializer_class(instance=request.user,
                                               data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'token invalid'}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionUserView(APIView):
    """Создание или удаление подписки на пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        action = request.data.get('action')
        if action:
            if subscribe_user(from_user=request.user,
                              to_user_username=username,
                              action=action):
                return Response(status=201)
        return Response(status=400)
