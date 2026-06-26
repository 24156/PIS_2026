from django.db import models

from academics.models import Enseignant, Filiere, Matiere, NiveauEtude


class EmploiDuTemps(models.Model):
    class Jour(models.TextChoices):
        LUNDI = 'lundi', 'Lundi'
        MARDI = 'mardi', 'Mardi'
        MERCREDI = 'mercredi', 'Mercredi'
        JEUDI = 'jeudi', 'Jeudi'
        VENDREDI = 'vendredi', 'Vendredi'
        SAMEDI = 'samedi', 'Samedi'

    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='emplois')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, related_name='emplois')
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='emplois')
    niveau = models.ForeignKey(NiveauEtude, on_delete=models.CASCADE, related_name='emplois')
    jour = models.CharField('Jour', max_length=20, choices=Jour.choices)
    heure_debut = models.TimeField('Heure de début')
    heure_fin = models.TimeField('Heure de fin')
    salle = models.CharField('Salle', max_length=100)
    annee_academique = models.CharField('Année académique', max_length=20, default='2025-2026')

    class Meta:
        verbose_name = 'Emploi du temps'
        verbose_name_plural = 'Emplois du temps'
        ordering = ['jour', 'heure_debut']

    def __str__(self):
        return f'{self.matiere.code} - {self.get_jour_display()} {self.heure_debut}'
