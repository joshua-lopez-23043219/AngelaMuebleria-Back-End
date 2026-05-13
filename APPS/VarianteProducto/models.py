from django.db import models

class VarianteProducto(models.Model):
    # Llave foránea hacia la app Producto
    producto = models.ForeignKey('Producto.Producto', on_delete=models.CASCADE, related_name='variantes')
    nombre_color = models.CharField(max_length=50)
    hex_color = models.CharField(max_length=7, help_text="#FFFFFF")
    ajuste_precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.producto.nombre} - {self.nombre_color}"

# Create your models here.
