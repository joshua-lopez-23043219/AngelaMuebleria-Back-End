from django.db import connection
from rest_framework.serializers import ModelSerializer

from Seguridad.Usuarios.models import Usuario


class SerializerUsuario (ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol',
                  'numero_telefono', 'municipio', 'direccion_exacta', 'is_active', 
                  'email_verificado', 'ultima_actividad', 'date_joined', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'ultima_actividad': {'read_only': True},
            'date_joined': {'read_only': True}
        }

    def create(self, validated_data):
        # Para forzar la verificación de correo, registramos al cliente como inactivo (is_active=False)
        rol = validated_data.get('rol', 'cliente')
        if rol == 'cliente':
            validated_data['is_active'] = False
            
        # Usamos create_user para que la contraseña se guarde encriptada
        return Usuario.objects.create_user(**validated_data)

