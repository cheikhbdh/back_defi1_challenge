from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.timezone import now
import datetime
import json
class CustomUser(AbstractUser):
    id_u = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    ROLE_CHOICES = [
        ('etudiant', 'etudiant'),
        ('admin', 'admin'),
        ('directeur', 'directeur'),
        ('comiteur', 'comiteur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')

    groups = models.ManyToManyField(Group, related_name="customuser_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



class PlageHoraire(models.Model):
    id_plh = models.AutoField(primary_key=True)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

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
            PlageHoraire.objects.get_or_create(heure_debut=debut, heure_fin=fin)


class Semaine(models.Model):
    id_s = models.AutoField(primary_key=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    annee = models.IntegerField()

    def save(self, *args, **kwargs):
        today = now().date()
        self.annee = today.year
        self.date_debut = today - datetime.timedelta(days=today.weekday())  # Lundi de la semaine actuelle
        self.date_fin = self.date_debut + datetime.timedelta(days=5)  # Samedi

        super(Semaine, self).save(*args, **kwargs)

        # Créer les jours de la semaine automatiquement
        for i in range(6):  # De lundi (0) à samedi (5)
            JourSemaine.objects.get_or_create(
                semaine=self, date_jour=self.date_debut + datetime.timedelta(days=i)
            )

# Modèle pour JourSemaine
class JourSemaine(models.Model):
    id_jrs = models.AutoField(primary_key=True)
    semaine = models.ForeignKey(Semaine, on_delete=models.CASCADE)
    date_jour = models.DateField()

    def __str__(self):
        return f"{self.date_jour} - Semaine {self.semaine.id_s}"

# Modèle pour Enseignant
class Enseignant(models.Model):
    id_Es = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    identifiant = models.CharField(max_length=100, unique=True)
    disponibilites = models.JSONField(default=list)  # Stocke les disponibilités en JSON

    def ajouter_disponibilite(self, date_jour, heure_debut, heure_fin):
        dispo = {"date_jour": str(date_jour), "heure_debut": str(heure_debut), "heure_fin": str(heure_fin)}
        self.disponibilites.append(dispo)
        self.save()

    def __str__(self):
        return self.nom
class Matiere(models.Model):
    FILIERE_CHOICES = [
        ('CNM', 'CNM'),
        ('RSS', 'RSS'),
        ('DSI', 'DSI'),
    ]
    nom = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    semestre = models.IntegerField()
    credits = models.FloatField()  # ECTS
    coefficient = models.FloatField()  # Pondération de la matière
    filiere = models.CharField(max_length=3, choices=FILIERE_CHOICES)  # Nouvelle colonne filiere

    def __str__(self):
        return f"{self.nom} (S{self.semestre}) - {self.get_filiere_display()}"

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
    matieres = models.ManyToManyField(Matiere)

    def __str__(self):
        return f"Groupe {self.nom} - {self.semestre}"

class SousGroupe(models.Model):
    groupe_parent = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="sous_groupes")
    groupe_enfant = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="groupe_parent")

    def __str__(self):
        return f"{self.groupe_enfant.nom} sous-groupe de {self.groupe_parent.nom}"


class ChargeHebdomadaire(models.Model):
    semaine = models.ForeignKey('Semaine', on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    cm_heures = models.IntegerField(default=0)  # Nombre de séances CM
    td_heures = models.IntegerField(default=0)  # Nombre de séances TD
    tp_heures = models.IntegerField(default=0)  # Nombre de séances TP
    reconduite = models.BooleanField(default=False)  # Si la config est reprise

    class Meta:
        unique_together = ('semaine', 'matiere', 'groupe')

    def __str__(self):
        return f"{self.matiere.nom} - {self.groupe.nom} - {self.semaine.nom}"


class AffectationEnseignant(models.Model):
    enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    TYPE_ENSEIGNEMENT = [
        ('CM', 'Cours Magistral'),
        ('TD', 'Travaux Dirigés'),
        ('TP', 'Travaux Pratiques'),
    ]
    type_enseignement = models.CharField(max_length=2, choices=TYPE_ENSEIGNEMENT)

    class Meta:
        unique_together = ('enseignant', 'groupe', 'matiere', 'type_enseignement')

    def __str__(self):
        return f"{self.enseignant.nom} - {self.matiere.nom} ({self.type_enseignement}) - {self.groupe.nom}"
    
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
