from typing import Dict

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from rest_framework import serializers
from Seguridad.Usuarios.models import Usuario


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get('password')

        # Buscar el usuario por email o username
        try:
            user = Usuario.objects.get(email=username)
        except Usuario.DoesNotExist:
            try:
                user = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                user = None

        if user is None:
            raise serializers.ValidationError({
                "detail": "No existe ninguna cuenta registrada con este correo electrónico o usuario."
            })

        # Validar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError({
                "detail": "La contraseña ingresada es incorrecta. Por favor, inténtalo de nuevo."
            })

        # Validar si la cuenta está activa y verificada
        if not user.is_active or not getattr(user, 'email_verificado', True):
            raise serializers.ValidationError({
                "detail": "Tu cuenta aún no está activa. Por favor, revisa tu correo electrónico para activarla."
            })

        data = super().validate(attrs)

        # Agregamos los datos del usuario a la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'name': self.user.first_name,
            'role': self.user.rol
        }

        return data