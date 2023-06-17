from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackEnd(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Check if the username is an email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Check if the username is a username
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user

        return None

    def get_username(self, email):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            return user.username
        except UserModel.DoesNotExist:
            return None
