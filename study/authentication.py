from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Device

class DeviceBoundJWTAuthentication(JWTAuthentication):
    """Require every API token to belong to an active registered device."""
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        device_id = token.get('device_id')
        if not device_id or not Device.objects.filter(device_id=device_id, is_active=True).exists():
            raise AuthenticationFailed('This device is not authorized. Unlock StudyMate again.')
        return user, token
