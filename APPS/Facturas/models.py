from django.db import models

from APPS import Pedidos


class Factura(models.Model):
    # Llave foránea hacia la app Pedido
    pedido = models.OneToOneField('Pedidos.Pedido', on_delete=models.CASCADE, related_name='factura')
    numero_factura = models.CharField(max_length=50, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    url_pdf = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Factura {self.numero_factura}"
# Create your models here.
