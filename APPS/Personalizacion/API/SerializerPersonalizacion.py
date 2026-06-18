from rest_framework import serializers
from APPS.Personalizacion.models import MuebleBase, ColorMaterial, MuebleColorModelo3D

class SerializerMuebleBase(serializers.ModelSerializer):
    class Meta:
        model = MuebleBase
        fields = '__all__'

class SerializerColorMaterial(serializers.ModelSerializer):
    class Meta:
        model = ColorMaterial
        fields = '__all__'

class SerializerMuebleColorModelo3D(serializers.ModelSerializer):
    mueble_base_name = serializers.CharField(source='mueble_base.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)
    color_hex = serializers.CharField(source='color.hex_code', read_only=True)
    model_3d_url = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    model_3d_url_read = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MuebleColorModelo3D
        fields = [
            'id', 'mueble_base', 'mueble_base_name',
            'color', 'color_name', 'color_hex',
            'model_3d_url', 'model_3d_url_read'
        ]

    def get_model_3d_url_read(self, obj):
        request = self.context.get('request')
        if obj.url_modelo_3d:
            if request is not None:
                return request.build_absolute_uri(obj.url_modelo_3d.url)
            return obj.url_modelo_3d.url
        return None

    def create(self, validated_data):
        model_3d_url = validated_data.pop('model_3d_url', None)
        if model_3d_url:
            relative_path = model_3d_url.split('/media/')[-1] if '/media/' in model_3d_url else model_3d_url
            validated_data['url_modelo_3d'] = relative_path
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'model_3d_url' in validated_data:
            model_3d_url = validated_data.pop('model_3d_url')
            if model_3d_url:
                relative_path = model_3d_url.split('/media/')[-1] if '/media/' in model_3d_url else model_3d_url
                instance.url_modelo_3d = relative_path
            else:
                instance.url_modelo_3d = None
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['model_3d_url'] = data.pop('model_3d_url_read')
        return data
