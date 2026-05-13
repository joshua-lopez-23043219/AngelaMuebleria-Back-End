from django.db import models

from APPS import ComboPedidos, Pedidos


class DetallePedido(models.Model):
    # Llaves foráneas apuntando a sus respectivas aplicaciones
    pedido = models.ForeignKey('Pedidos.Pedido', on_delete=models.CASCADE, related_name='detalles')
    combo = models.ForeignKey('ComboPedidos.ComboPedido', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='items')
    producto = models.ForeignKey('Producto.Producto', on_delete=models.CASCADE)
    variante = models.ForeignKey('VarianteProducto.VarianteProducto', on_delete=models.SET_NULL, null=True, blank=True)

    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    es_regalo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} (Pedido {self.pedido.id})"
# Create your models here.
