from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import (
    RegisterView, LoginView, UserView, LogoutView, VerifierEmailView,
    PlageHoraireViewSet, SemaineViewSet, JourSemaineViewSet, EnseignantViewSet,
    MatiereViewSet, GroupeViewSet, SousGroupeViewSet, ChargeHebdomadaireViewSet,
    AffectationEnseignantViewSet, generer_emploi_du_temps, telecharger_emploi_excel, telecharger_emploi_pdf
)


router = DefaultRouter()
router.register(r'plages-horaires', PlageHoraireViewSet, basename='plage-horaire')
router.register(r'semaines', SemaineViewSet, basename='semaine')
router.register(r'jours-semaine', JourSemaineViewSet, basename='jour-semaine')
router.register(r'enseignants', EnseignantViewSet, basename='enseignant')
router.register(r'matieres', MatiereViewSet)
router.register(r'groupes', GroupeViewSet)
router.register(r'sous_groupes', SousGroupeViewSet)
router.register(r'charges_hebdomadaires', ChargeHebdomadaireViewSet)
router.register(r'affectations_enseignants', AffectationEnseignantViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentification
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('verify-email/', VerifierEmailView.as_view(), name='verify-email'),

    # API REST
    path('api/', include(router.urls)),

    # Génération et téléchargement de l'emploi du temps
    path('generer-emploi-du-temps/', generer_emploi_du_temps, name='generer-emploi-du-temps'),
    path('telecharger-emploi-excel/<int:groupe_id>/', telecharger_emploi_excel, name='telecharger-emploi-excel'),
    path('telecharger-emploi-pdf/<int:groupe_id>/', telecharger_emploi_pdf, name='telecharger-emploi-pdf'),
]
