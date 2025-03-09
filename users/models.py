from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.timezone import now
import datetime
import json
from django.db.utils import IntegrityError
class CustomUser(AbstractUser):
    id_u = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    ROLE_CHOICES = [
        ('professeur', 'professeur'),
        ('admin', 'admin'),
        ('directeur', 'directeur'),
      
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='professeur')

    groups = models.ManyToManyField(Group, related_name="customuser_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class PlageHoraire(models.Model):
    id_plh = models.AutoField(primary_key=True)
    heure_debut = models.TimeField(unique=True)
    heure_fin = models.TimeField(unique=True)

    def __str__(self):
        return f"{self.heure_debut} - {self.heure_fin}"

    @staticmethod
    def initialiser_plages():
        plages_fixes = [
            ("08:00", "09:30"),
            ("09:45", "11:15"),
            ("11:30", "13:00"),
            ("15:00", "16:30"),
            ("17:00", "18:30"),
        ]
        for debut, fin in plages_fixes:
            try:
                PlageHoraire.objects.create(heure_debut=debut, heure_fin=fin)
            except IntegrityError:
                pass  # Ignore si la plage existe déjà


class Semaine(models.Model):
    id_s = models.AutoField(primary_key=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    annee = models.IntegerField()

    def save(self, *args, **kwargs):
        today = now().date()

        # Vérifier s'il existe déjà une semaine en base
        derniere_semaine = Semaine.objects.order_by('-date_debut').first()

        if derniere_semaine:
            prochain_lundi = derniere_semaine.date_debut + datetime.timedelta(days=7)
        else:
            # Si aucune semaine n'existe, prendre le lundi actuel
            prochain_lundi = today - datetime.timedelta(days=today.weekday())

        self.annee = prochain_lundi.year
        self.date_debut = prochain_lundi
        self.date_fin = prochain_lundi + datetime.timedelta(days=5)  # Samedi

        super(Semaine, self).save(*args, **kwargs)

        # Créer automatiquement les jours de la semaine
        for i in range(6):  # De lundi à samedi
            JourSemaine.objects.get_or_create(
                semaine=self, date_jour=self.date_debut + datetime.timedelta(days=i)
            )

    def __str__(self):
        return f"Semaine {self.date_debut} - {self.date_fin}"


# Modèle JourSemaine
class JourSemaine(models.Model):
    id_jrs = models.AutoField(primary_key=True)
    semaine = models.ForeignKey(Semaine, on_delete=models.CASCADE)
    date_jour = models.DateField(unique=True)  # Empêche la duplication

    def __str__(self):
        return f"{self.date_jour} - Semaine {self.semaine.id_s}"
# Modèle pour Enseignant
from django.utils.timezone import now
import datetime
from django.db.utils import IntegrityError
from django.db import models

class Enseignant(models.Model):
    id_Es = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    identifiant = models.CharField(max_length=100, unique=True)
    disponibilites = models.JSONField(default=list)
    modifications_ouvertes = models.BooleanField(default=False)  # Stocke l'état des modifications

    def mettre_a_jour_modifications(self):
        """Met à jour le champ `modifications_ouvertes` chaque samedi."""
        today = now().date()
        lundi_semaine_actuelle = today - datetime.timedelta(days=today.weekday())  # Lundi actuel
        samedi_suivant = lundi_semaine_actuelle + datetime.timedelta(days=6)  # Samedi suivant

        self.modifications_ouvertes = today >= samedi_suivant
        self.save()

    def ajouter_disponibilite(self, date_jour, heure_debut, heure_fin):
        """Ajoute une disponibilité si la modification est autorisée."""
        if not self.modifications_ouvertes:
            raise IntegrityError("Vous pourrez modifier vos disponibilités à partir de samedi.")

        # Ajouter la nouvelle disponibilité
        self.disponibilites.append({
            "date_jour": str(date_jour),
            "heure_debut": str(heure_debut),
            "heure_fin": str(heure_fin)
        })
        self.save()

    def __str__(self):
        return self.nom

    
class Filiere(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class Matiere(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    semestre = models.IntegerField()
    credits = models.FloatField()
    coefficient = models.FloatField()
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name="matieres")

    def __str__(self):
        return f"{self.nom} (S{self.semestre}) - {self.filiere.nom}"



# Modèle Groupe (lié à une Filière)
class Groupe(models.Model):
    SEMESTRE_CHOICES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
        ('S3', 'Semestre 3'),
        ('S4', 'Semestre 4'),
        ('S5', 'Semestre 5'),
    ]
    nom = models.CharField(max_length=50, unique=True)
    semestre = models.CharField(max_length=2, choices=SEMESTRE_CHOICES)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name="groupes")
    
    def __str__(self):
        return f"Groupe {self.nom} - {self.semestre} ({self.filiere.nom})"




class ChargeHebdomadaire(models.Model):
    semaine = models.ForeignKey('Semaine', on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, null=True, blank=True)  # Pour CM
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)  # Pour TD/TP

    cm_heures = models.IntegerField(default=0)  # Nombre d'heures de CM (lié à la filière)
    td_heures = models.IntegerField(default=0)  # Nombre d'heures de TD (lié au groupe)
    tp_heures = models.IntegerField(default=0)  # Nombre d'heures de TP (lié au groupe)
    
    reconduite = models.BooleanField(default=False)  # Si la configuration est reprise

    class Meta:
        unique_together = ('semaine', 'matiere', 'filiere', 'groupe')

    def save(self, *args, **kwargs):
        if self.cm_heures > 0:
            self.groupe = None  # Un CM est lié à une filière, pas à un groupe
        if self.td_heures > 0 or self.tp_heures > 0:
            self.filiere = None  # Un TD ou TP est lié à un groupe, pas à une filière
        
        super().save(*args, **kwargs)

    def __str__(self):
        if self.filiere:
            return f"{self.matiere.nom} - {self.filiere.nom} (CM) - Semaine {self.semaine.id_s}"
        return f"{self.matiere.nom} - {self.groupe.nom} (TD/TP) - Semaine {self.semaine.id_s}"


class AffectationEnseignant(models.Model):
    enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    
    TYPE_ENSEIGNEMENT = [
        ('CM', 'Cours Magistral'),
        ('TD', 'Travaux Dirigés'),
        ('TP', 'Travaux Pratiques'),
    ]
    type_enseignement = models.CharField(max_length=2, choices=TYPE_ENSEIGNEMENT)

    # CM → Filière, TD/TP → Groupe
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, null=True, blank=True)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('enseignant', 'matiere', 'type_enseignement', 'filiere', 'groupe')

    def save(self, *args, **kwargs):
        if self.type_enseignement == "CM":
            self.groupe = None
        else:
            self.filiere = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enseignant.nom} - {self.matiere.nom} ({self.type_enseignement})"
    
class Salle(models.Model):
    id_sl = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)

    def __str__(self):
        return f"Salle {self.nom}"

class EmploiDuTemps(models.Model):
    id_e = models.AutoField(primary_key=True)
    groupe = models.ForeignKey('Groupe', on_delete=models.CASCADE)
    enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE)
    matiere = models.ForeignKey('Matiere', on_delete=models.CASCADE)
    plage_horaire = models.ForeignKey('PlageHoraire', on_delete=models.CASCADE)
    salle = models.ForeignKey('Salle', on_delete=models.CASCADE, null=True, blank=True)
    jour = models.ForeignKey('JourSemaine', on_delete=models.CASCADE)  # Lien avec JourSemaine
    heure_debut_cours = models.TimeField()
    heure_fin_cours = models.TimeField()

    class Meta:
        unique_together = ('groupe', 'plage_horaire', 'jour') 

    def __str__(self):
        return f"{self.groupe.nom} - {self.matiere.nom} ({self.enseignant.nom}) - {self.plage_horaire} - {self.jour.date_jour}"
