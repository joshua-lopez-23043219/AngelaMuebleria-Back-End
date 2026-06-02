from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    OPCIONES_ROL = (
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=10, choices=OPCIONES_ROL, default='cliente')
    numero_telefono = models.CharField(max_length=20, blank=True, null=True)

    municipio = models.ForeignKey('Municipio.Municipio', on_delete=models.SET_NULL, null=True, blank=True)
    direccion_exacta = models.TextField(help_text="Barrio, calle, nro de casa", blank=True, null=True)

    # NUEVO CAMPO: Para la confirmación de cuenta
    email_verificado = models.BooleanField(default=False,
                                           help_text="Se marca como True cuando el cliente hace clic en el enlace del correo")
    
    # NUEVO CAMPO: Para rastrear estado en tiempo real (Online/Offline)
    ultima_actividad = models.DateTimeField(null=True, blank=True,
                                            help_text="Fecha y hora del último request del usuario")

    def save(self, *args, **kwargs):
        # Magia: Si alguien es creado como superusuario por consola, asignarle el rol de admin automáticamente
        if self.is_superuser and self.rol != 'admin':
            self.rol = 'admin'
            self.email_verificado = True # Un admin no necesita verificar su correo
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.rol}"
