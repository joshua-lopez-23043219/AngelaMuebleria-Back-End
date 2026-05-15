from rest_framework import serializers
from APPS.Producto.models import Producto

class SerializerProducto(serializers.ModelSerializer):
    # Campos que espera el frontend
    name = serializers.CharField(source='nombre')
    price = serializers.DecimalField(source='precio_base', max_digits=10, decimal_places=2)
    image_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['id', 'name', 'price', 'descripcion', 'image_url', 'category', 'stock', 'esta_activo']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.url_miniatura:
            if request is not None:
                return request.build_absolute_uri(obj.url_miniatura.url)
            return obj.url_miniatura.url
        return None

    def get_category(self, obj):
        return obj.categoria.nombre if obj.categoria else 'General'
