from ..models import CustomUser
from .users_range_service import get_user_object
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def send_confirm_password_reset_email(request: HttpRequest) -> int:
    """
    Функция отправляет email со ссылкой, подтверждающей смену пароля.
    Ссылка включает закодированное имя пользователя и токен
    test
    """
    username = request.data.get('username')
    user = get_user_object(username)
    if user:
        confirm_password_reset_url = _get_confirm_reset_url(request,
                                                            *_get_uid_and_token(user))
        confirm_email_theme = 'Сброс пароля на blogging-platform'
        confirm_email_body = f'Для сброса пароля к аккаунту {username} ' \
                             f'используйте ссылку: {confirm_password_reset_url}'
        return send_mail(subject=confirm_email_theme,
                         message=confirm_email_body,
                         from_email='next_one_blog@polarmail.com',
                         recipient_list=[user.email])


def check_confirm_reset_data(uidb64: str, token: str) -> bool:
    """Проверка токена для сброса пароля"""
    username = smart_str(urlsafe_base64_decode(uidb64))
    user = get_user_object(username)
    if PasswordResetTokenGenerator().check_token(user, token):
        return True
    return False


def _get_uid_and_token(user: CustomUser) -> tuple[str, str]:
    uidb64 = urlsafe_base64_encode(smart_bytes(user.username))
    token = PasswordResetTokenGenerator().make_token(user)
    return uidb64, token


def _get_confirm_reset_url(request: HttpRequest, uidb64: str, token: str) -> str:
    """Генерация ссылки"""
    return request.build_absolute_uri(
            reverse_lazy('password_reset_confirm', kwargs={
                'uidb64': uidb64,
                'token': token
            })
    )
