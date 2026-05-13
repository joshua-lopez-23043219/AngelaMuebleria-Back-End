from django.db import connection
from rest_framework.serializers import ModelSerializer

from Seguridad.Usuarios.models import Usuario


class SerializerUsuario (ModelSerializer):
    class Meta:
        model = Usuario
        # No devolvemos el password por seguridad en GET, pero permitimos escribirlo
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol',
                  'numero_telefono', 'municipio', 'direccion_exacta', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usamos create_user para que la contraseña se guarde encriptada
        return Usuario.objects.create_user(**validated_data)

