from django.db import models

class MuebleBase(models.Model):
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=500)
    wood_type = models.CharField(max_length=100, default='N/A')
    dimensions = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.name

class ColorMaterial(models.Model):
    OPCIONES_TIPO = (
        ('paint', 'Pintura/Acabado'),
        ('fabric', 'Tela/Tapizado'),
    )
    name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7, help_text="Ej: #FFFFFF")
    type = models.CharField(max_length=20, choices=OPCIONES_TIPO, default='paint')
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class MuebleColorModelo3D(models.Model):
    mueble_base = models.ForeignKey('Personalizacion.MuebleBase', on_delete=models.CASCADE, related_name='modelos_color')
    color = models.ForeignKey('Personalizacion.ColorMaterial', on_delete=models.CASCADE, related_name='modelos_mueble')
    url_modelo_3d = models.FileField(upload_to='personalizacion/modelos_color/', null=True, blank=True)

    class Meta:
        unique_together = ('mueble_base', 'color')

    def __str__(self):
        return f"{self.mueble_base.name} - {self.color.name}"
