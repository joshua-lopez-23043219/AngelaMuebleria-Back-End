import threading

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import Usuario



@receiver(post_save, sender=Usuario)
def enviar_correo_activacion(sender, instance, created, **kwargs):
    if created and instance.rol == 'cliente':
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        enlace_activacion = f"https://web-production-93930.up.railway.app/apiUsuarios/Usuario/activar/{uid}/{token}/"
        asunto = "Confirma tu cuenta en ANGELA MUEBLERIA"
        mensaje = f"Hola {instance.username},\n\nGracias por registrarte. Para activar tu cuenta, haz clic en el siguiente enlace:\n\n{enlace_activacion}"
        # --- CAMBIO AQUÍ: Función interna para el hilo ---
        def send_email_thread():
            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.EMAIL_HOST_USER,
                    [instance.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando correo: {e}")
        # Iniciamos el hilo para que no bloquee el registro
        threading.Thread(target=send_email_thread).start()