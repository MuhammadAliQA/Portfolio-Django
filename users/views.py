from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .serializers import RegisterSerializer, UserSerializer


# Login da full_name ham qaytarish uchun custom serializer
class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Allow login via email as well as username.
        email = attrs.pop('email', None)
        username = (attrs.get('username') or email or '').strip()
        if username:
            try:
                user = User.objects.get(username__iexact=username)
                attrs['username'] = user.get_username()
            except User.DoesNotExist:
                if '@' in username:
                    try:
                        user = User.objects.get(email__iexact=username)
                        attrs['username'] = user.get_username()
                    except User.DoesNotExist:
                        pass
        data = super().validate(attrs)
        data['user'] = {
            'id':       self.user.id,
            'username': self.user.username,
            'email':    self.user.email,
            'role':     self.user.role,
            'full_name': self.user.get_full_name(),
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """Login bo'lgan foydalanuvchi o'z profilini ko'radi/tahrirlaydi."""
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
