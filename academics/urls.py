from django.urls import path

from . import views

app_name = 'academics'

urlpatterns = [
    path('facultes/', views.faculte_list, name='faculte_list'),
    path('facultes/create/', views.faculte_create, name='faculte_create'),
    path('facultes/<int:pk>/edit/', views.faculte_edit, name='faculte_edit'),
    path('facultes/<int:pk>/delete/', views.faculte_delete, name='faculte_delete'),
    path('departements/', views.departement_list, name='departement_list'),
    path('departements/create/', views.departement_create, name='departement_create'),
    path('departements/<int:pk>/edit/', views.departement_edit, name='departement_edit'),
    path('departements/<int:pk>/delete/', views.departement_delete, name='departement_delete'),
    path('filieres/', views.filiere_list, name='filiere_list'),
    path('filieres/create/', views.filiere_create, name='filiere_create'),
    path('filieres/<int:pk>/edit/', views.filiere_edit, name='filiere_edit'),
    path('filieres/<int:pk>/delete/', views.filiere_delete, name='filiere_delete'),
    path('niveaux/', views.niveau_list, name='niveau_list'),
    path('niveaux/create/', views.niveau_create, name='niveau_create'),
    path('niveaux/<int:pk>/edit/', views.niveau_edit, name='niveau_edit'),
    path('niveaux/<int:pk>/delete/', views.niveau_delete, name='niveau_delete'),
    path('matieres/', views.matiere_list, name='matiere_list'),
    path('matieres/create/', views.matiere_create, name='matiere_create'),
    path('matieres/<int:pk>/edit/', views.matiere_edit, name='matiere_edit'),
    path('matieres/<int:pk>/delete/', views.matiere_delete, name='matiere_delete'),
    path('enseignants/', views.enseignant_list, name='enseignant_list'),
    path('enseignants/create/', views.enseignant_create, name='enseignant_create'),
    path('enseignants/<int:pk>/edit/', views.enseignant_edit, name='enseignant_edit'),
    path('enseignants/<int:pk>/delete/', views.enseignant_delete, name='enseignant_delete'),
    path('etudiants/', views.etudiant_list, name='etudiant_list'),
    path('etudiants/create/', views.etudiant_create, name='etudiant_create'),
    path('etudiants/<int:pk>/edit/', views.etudiant_edit, name='etudiant_edit'),
    path('etudiants/<int:pk>/delete/', views.etudiant_delete, name='etudiant_delete'),
]
