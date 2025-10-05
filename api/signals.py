from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Challenge

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un UserProfile automáticamente cada vez que se crea un nuevo usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=Challenge)
def award_points_on_challenge_completion(sender, instance, **kwargs):
    """
    Suma los puntos de un reto al perfil del usuario cuando su estado
    cambia a 'completed' y los puntos no han sido otorgados previamente.
    """
    # Comprobamos si el reto está completado y si los puntos aún no se han sumado.
    if instance.status == 'completed' and not instance.points_awarded:
        try:
            # Obtenemos el perfil del usuario y sumamos los puntos.
            profile = instance.user.profile
            profile.total_points += instance.awarded_points
            profile.save()

            # Marcamos el reto para que no vuelva a sumar puntos.
            # Usamos update_fields para evitar una señal recursiva infinita.
            instance.points_awarded = True
            instance.save(update_fields=['points_awarded'])

        except UserProfile.DoesNotExist:
            # Manejo de caso borde: si el perfil no existe, no hacemos nada.
            pass