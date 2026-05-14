from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import Usuario


# El decorador @receiver le dice a la función que "escuche" al modelo Usuario
@receiver(post_save, sender=Usuario)
def enviar_correo_activacion(sender, instance, created, **kwargs):
    # IMPORTANTE: Solo queremos enviar el correo si el usuario es NUEVO (created = True)
    # y si su rol es 'cliente' (no queremos mandarle esto a los administradores)
    if created and instance.rol == 'cliente':
        # 1. Generamos el código criptográfico único para este usuario
        token = default_token_generator.make_token(instance)
        # 2. Codificamos su ID para enviarlo seguro por la URL
        uid = urlsafe_base64_encode(force_bytes(instance.pk))

        # 3. Armamos el enlace que el cliente va a clickear
        # (Ese localhost cambiará por tu dominio real cuando subas la página a internet)
        enlace_activacion = f"http://localhost:8000/api/usuarios/activar/{uid}/{token}/"

        # 4. Redactamos y enviamos el correo
        asunto = "Confirma tu cuenta en ANGELA MUEBLERIA"
        mensaje = f"Hola {instance.username},\n\nGracias por registrarte. Para activar tu cuenta y poder hacer pedidos, haz clic en el siguiente enlace:\n\n{enlace_activacion}"

        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,  # El correo de tu mueblería (configurado en settings.py)
            [instance.email],  # El correo del cliente
            fail_silently=True,
        )