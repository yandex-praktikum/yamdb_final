from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

from .messages import subject, from_email, message
from reviews.models import User


def get_user_or_false(data):
    if User.objects.filter(username=data['username'], email=data['email']):
        return User.objects.get(username=data['username'], email=data['email'])
    return False


def validate_request_data(data):
    not_provided_fields = {}
    for arg in ('username', 'email'):
        if not data.get(arg):
            not_provided_fields[arg] = ['This field is required.']
    if not_provided_fields:
        raise ValidationError(not_provided_fields)
    user = get_user_or_false(data)
    error = ''
    if not user:
        if User.objects.filter(username=data['username']).exists():
            error = (
                'username: ["Уже существует пользователь с таким '
                'именем пользователя и другим e-mail]"'
            )
        if User.objects.filter(email=data['email']).exists():
            error = (
                'email: ["Уже существует пользователь с таким '
                'e-mail и другим именем пользователя"]'
            )
    if error:
        raise ValidationError(error)


def send_confirmation_email(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject,
        message.format(code=confirmation_code),
        from_email,
        [user.email],
        fail_silently=False,
    )
