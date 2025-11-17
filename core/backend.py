# core/backend.py
from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class EmailBackend(ModelBackend):
    """
    Permite autenticar usando email en lugar de username (usado por Django por defecto)
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
