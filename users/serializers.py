from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser
from .models import PlageHoraire, Semaine, JourSemaine, Enseignant
from .models import Matiere, Groupe, SousGroupe, ChargeHebdomadaire, AffectationEnseignant
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id_u', 'login', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance



class PlageHoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlageHoraire
        fields = '__all__'

class SemaineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semaine
        fields = '__all__'

class JourSemaineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JourSemaine
        fields = '__all__'

class EnseignantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enseignant
        fields = '__all__'



class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ['id', 'nom', 'code', 'semestre', 'credits', 'coefficient']


class GroupeSerializer(serializers.ModelSerializer):
    matieres = MatiereSerializer(many=True)

    class Meta:
        model = Groupe
        fields = ['id', 'nom', 'semestre', 'matieres']


class SousGroupeSerializer(serializers.ModelSerializer):
    groupe_parent = GroupeSerializer()
    groupe_enfant = GroupeSerializer()

    class Meta:
        model = SousGroupe
        fields = ['id', 'groupe_parent', 'groupe_enfant']


class ChargeHebdomadaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeHebdomadaire
        fields = ['id', 'semaine', 'matiere', 'groupe', 'cm_heures', 'td_heures', 'tp_heures', 'reconduite']


class AffectationEnseignantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffectationEnseignant
        fields = ['id', 'enseignant', 'groupe', 'matiere', 'type_enseignement']
