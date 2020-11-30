from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthBackend(ModelBackend):
    def authenticate(self, email=None):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
