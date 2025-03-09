from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Semaine,PlageHoraire

@receiver(post_migrate)
def create_initial_semaine(sender, **kwargs):
    if sender.name == "users":  # Remplacez par votre nom d'application
        if not Semaine.objects.exists():
            Semaine().save()  # Crée la première semaine automatiquement
@receiver(post_migrate)
def create_fixed_plages(sender, **kwargs):
    if sender.name == "users":  # Remplacez par le nom de votre app
        PlageHoraire.initialiser_plages()
