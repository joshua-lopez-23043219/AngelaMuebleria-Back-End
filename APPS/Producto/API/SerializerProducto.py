from rest_framework import serializers
import random
from APPS.Producto.models import Producto
from APPS.Categoria.models import Categoria

class SerializerProducto(serializers.ModelSerializer):
    # Campos para lectura/escritura amigables con el frontend
    name = serializers.CharField(source='nombre')
    price = serializers.DecimalField(source='precio_base', max_digits=10, decimal_places=2)
    image_url = serializers.CharField(write_only=True, required=False, allow_null=True)
    category = serializers.CharField(write_only=True, required=False, allow_null=True)
    description = serializers.CharField(source='descripcion', required=False, allow_blank=True, allow_null=True)
    
    # Campo solo lectura para mostrar URL real
    image_url_read = serializers.SerializerMethodField(source='get_image_url_read')
    category_read = serializers.SerializerMethodField(source='get_category_read')
    
    class Meta:
        model = Producto
        fields = ['id', 'name', 'price', 'description', 'image_url', 'image_url_read', 'category', 'category_read', 'stock', 'esta_activo']

    def get_image_url_read(self, obj):
        request = self.context.get('request')
        if obj.url_miniatura:
            if request is not None:
                return request.build_absolute_uri(obj.url_miniatura.url)
            return obj.url_miniatura.url
        return None

    def get_category_read(self, obj):
        return obj.categoria.nombre if obj.categoria else 'General'

    def create(self, validated_data):
        # Generar código de producto único
        codigo = f"PROD-{random.randint(1000, 99999)}"
        validated_data['codigo_producto'] = codigo
        
        # Manejo de imagen
        image_url = validated_data.pop('image_url', None)
        if image_url:
            # Extraer solo el path relativo
            relative_path = image_url.split('/media/')[-1] if '/media/' in image_url else image_url
            validated_data['url_miniatura'] = relative_path

        # Manejo de categoría
        category_name = validated_data.pop('category', None)
        if category_name:
            cat, created = Categoria.objects.get_or_create(nombre=category_name)
            validated_data['categoria'] = cat

        return super().create(validated_data)

    def update(self, instance, validated_data):
        image_url = validated_data.pop('image_url', None)
        if image_url:
            relative_path = image_url.split('/media/')[-1] if '/media/' in image_url else image_url
            instance.url_miniatura = relative_path

        category_name = validated_data.pop('category', None)
        if category_name:
            cat, created = Categoria.objects.get_or_create(nombre=category_name)
            instance.categoria = cat

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        # Mapear los campos de lectura de vuelta a los nombres que espera el frontend
        data = super().to_representation(instance)
        data['image_url'] = data.pop('image_url_read')
        data['category'] = data.pop('category_read')
        return data
