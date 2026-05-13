import random
import string
from django.db import models

class Suscriptor(models.Model):
    # Solo pedimos el correo, y debe ser único para que no pidan 20 códigos con el mismo email
    email = models.EmailField(unique=True, help_text="Correo del cliente suscrito")

    # El código se generará automáticamente
    codigo_descuento = models.CharField(max_length=20, unique=True, blank=True)

    # Podemos definir de cuánto es el premio (ej. 10% o 15% de descuento)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    # Para saber si ya lo gastaron en una compra
    fue_usado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    # MAGIA: Generación del código aleatorio
    def save(self, *args, **kwargs):
        # Si es un suscriptor nuevo y no tiene código todavía...
        if not self.codigo_descuento:
            # Creamos un abecedario de letras mayúsculas y números
            caracteres = string.ascii_uppercase + string.digits

            # Elegimos 6 caracteres al azar
            codigo_aleatorio = ''.join(random.choice(caracteres) for i in range(6))

            # Armamos el código final (Ejemplo: DESC-X7B9Q2)
            self.codigo_descuento = f"DESC-{codigo_aleatorio}"

        # Guardamos en la base de datos
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.codigo_descuento}"
# Create your models here.
