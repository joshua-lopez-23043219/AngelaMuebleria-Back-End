from django.db import models

from APPS import Pedidos


class ComboPedido(models.Model):
    # Llave foránea hacia la app Pedido
    pedido = models.ForeignKey('Pedidos.Pedido', on_delete=models.CASCADE, related_name='combos')
    nombre = models.CharField(max_length=255, help_text="Ej: Combo 4 Sillas + Mesa")
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - Pedido {self.pedido.id}"
# Create your models here.
