from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


UserModel = get_user_model()


class PermissiveModelBackend(BaseBackend):
    def get_user(self, user_id):
        return UserModel.objects.get(id=user_id)

    def authenticate(self, request, username=None, password=None):
        user, created = UserModel.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
            user.save()
        if user.is_active:
            return user
