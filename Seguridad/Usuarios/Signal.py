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
    print(f"DEBUG: Signal activado para {instance.email}. Creado: {created}, Rol: {instance.rol}")
    if created and str(instance.rol).lower() == 'cliente':
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        enlace_activacion = f"https://api.angelamuebleria.business/apiUsuarios/Usuario/activar/{uid}/{token}/"
        asunto = "Confirma tu cuenta en ANGELA MUEBLERIA"
        mensaje_texto = f"Hola {instance.username},\n\nGracias por registrarte en Mueblería Ángela. Para activar tu cuenta, haz clic en el siguiente enlace:\n\n{enlace_activacion}"
        
        mensaje_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #2c3e50; text-align: center;">¡Bienvenido a Mueblería Ángela!</h2>
                <p>Hola <strong>{instance.username}</strong>,</p>
                <p>Gracias por registrarte con nosotros. Estamos felices de tenerte.</p>
                <p>Para activar tu cuenta y poder iniciar sesión, por favor haz clic en el siguiente botón:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{enlace_activacion}" style="background-color: #27ae60; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Activar Mi Cuenta</a>
                </div>
                <p style="font-size: 12px; color: #7f8c8d; text-align: center;">Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
                <p style="font-size: 12px; color: #7f8c8d; text-align: center; word-break: break-all;">{enlace_activacion}</p>
            </body>
        </html>
        """

        # --- CAMBIO AQUÍ: Función interna para el hilo ---
        def send_email_thread():
            try:
                send_mail(
                    subject=asunto,
                    message=mensaje_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    html_message=mensaje_html,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando correo: {e}")
        # Iniciamos el hilo para que no bloquee el registro
        threading.Thread(target=send_email_thread).start()