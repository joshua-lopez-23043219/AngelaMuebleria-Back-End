from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from APPS.ComboPedidos.models import ComboPedido, ReglaCombo


class SerializerComboPedido (ModelSerializer):
    class Meta:
        model = ComboPedido
        fields ='__all__'


class SerializerReglaCombo(ModelSerializer):
    producto_requerido_nombre = serializers.SerializerMethodField()
    producto_asociado_nombre = serializers.SerializerMethodField()
    productos_detalle = serializers.SerializerMethodField()
    imagen_url = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    imagen_url_read = serializers.SerializerMethodField(method_name='get_imagen_url_read')

    class Meta:
        model = ReglaCombo
        fields = '__all__'

    def get_imagen_url_read(self, obj):
        request = self.context.get('request')
        if obj.imagen:
            if request is not None:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None

    def create(self, validated_data):
        imagen_url = validated_data.pop('imagen_url', None)
        if imagen_url:
            relative_path = imagen_url.split('/media/')[-1] if '/media/' in imagen_url else imagen_url
            validated_data['imagen'] = relative_path
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'imagen_url' in validated_data:
            imagen_url = validated_data.pop('imagen_url')
            if imagen_url:
                relative_path = imagen_url.split('/media/')[-1] if '/media/' in imagen_url else imagen_url
                instance.imagen = relative_path
            else:
                instance.imagen = None
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['imagen_url'] = data.pop('imagen_url_read')
        return data

    def get_producto_requerido_nombre(self, obj):
        if obj.producto_requerido:
            return obj.producto_requerido.nombre
        return "Producto no asignado"

    def get_producto_asociado_nombre(self, obj):
        if obj.producto_asociado:
            return obj.producto_asociado.nombre
        return "Producto no asignado"

    def get_productos_detalle(self, obj):
        import json
        from APPS.Producto.models import Producto
        if not obj.productos_json:
            # Fallback a los campos antiguos para compatibilidad
            res = []
            if obj.producto_requerido:
                res.append({
                    'id': obj.producto_requerido.id,
                    'nombre': obj.producto_requerido.nombre,
                    'precio_base': float(obj.producto_requerido.precio_base),
                    'url_miniatura': obj.producto_requerido.url_miniatura.url if obj.producto_requerido.url_miniatura else None,
                    'cantidad': obj.cantidad_requerida or 1
                })
            if obj.producto_asociado:
                res.append({
                    'id': obj.producto_asociado.id,
                    'nombre': obj.producto_asociado.nombre,
                    'precio_base': float(obj.producto_asociado.precio_base),
                    'url_miniatura': obj.producto_asociado.url_miniatura.url if obj.producto_asociado.url_miniatura else None,
                    'cantidad': obj.cantidad_asociado or 1
                })
            return res
            
        try:
            items = json.loads(obj.productos_json)
            res = []
            for item in items:
                pid = item.get('producto_id') or item.get('id')
                qty = item.get('cantidad') or item.get('quantity') or 1
                if not pid:
                    continue
                try:
                    p = Producto.objects.get(id=pid)
                    res.append({
                        'id': p.id,
                        'nombre': p.nombre,
                        'precio_base': float(p.precio_base),
                        'url_miniatura': p.url_miniatura.url if p.url_miniatura else None,
                        'cantidad': int(qty)
                    })
                except Producto.DoesNotExist:
                    continue
            return res
        except Exception:
            return []

