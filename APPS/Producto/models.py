from django.db import models


class Producto(models.Model):
    OPCIONES_TIPO = (
        ('silla', 'Silla'),
        ('mesa', 'Mesa'),
        ('sofa', 'Sofá'),
        ('cama', 'Cama'),
        ('armario', 'Armario/Gabinete'),
        ('otro', 'Otro'),
    )

    nombre = models.CharField(max_length=255)
    codigo_producto = models.CharField(max_length=50, unique=True, help_text="Código único de inventario")
    tipo_producto = models.CharField(max_length=20, choices=OPCIONES_TIPO, default='otro')

    # Llave foránea hacia la app Categoria
    categoria = models.ForeignKey('Categoria.Categoria', on_delete=models.SET_NULL, null=True, related_name='productos')

    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    esta_activo = models.BooleanField(default=True, help_text="Desmarcar para ocultar de la web")

    descripcion = models.TextField(blank=True, null=True)
    materiales = models.CharField(max_length=200, blank=True)
    dimensiones = models.CharField(max_length=100, blank=True)


    url_miniatura = models.ImageField(upload_to='productos/miniaturas/', null=True, blank=True)
    url_modelo_3d = models.FileField(upload_to='productos/modelos_3d/', null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.codigo_producto}] {self.nombre}"

# Create your models here.
