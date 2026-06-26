from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from academics.models import Etudiant, Matiere


class Cours(models.Model):
    titre = models.CharField('Titre', max_length=300)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='cours')
    enseignant = models.ForeignKey(
        'academics.Enseignant', on_delete=models.CASCADE, related_name='cours'
    )
    fichier = models.FileField('Fichier', upload_to='cours/', blank=True, null=True)
    description = models.TextField('Description', blank=True)
    annee_academique = models.CharField('Année académique', max_length=20, default='2025-2026')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre


class TravailDirige(models.Model):
    titre = models.CharField('Titre', max_length=300)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='tds')
    enseignant = models.ForeignKey(
        'academics.Enseignant', on_delete=models.CASCADE, related_name='tds'
    )
    fichier = models.FileField('Fichier', upload_to='td/', blank=True, null=True)
    description = models.TextField('Description', blank=True)
    date_publication = models.DateField('Date de publication', auto_now_add=True)

    class Meta:
        verbose_name = 'Travail Dirigé (TD)'
        verbose_name_plural = 'Travaux Dirigés (TD)'
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre


class TravailPratique(models.Model):
    titre = models.CharField('Titre', max_length=300)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='tps')
    enseignant = models.ForeignKey(
        'academics.Enseignant', on_delete=models.CASCADE, related_name='tps'
    )
    fichier = models.FileField('Fichier', upload_to='tp/', blank=True, null=True)
    description = models.TextField('Description', blank=True)
    date_publication = models.DateField('Date de publication', auto_now_add=True)

    class Meta:
        verbose_name = 'Travail Pratique (TP)'
        verbose_name_plural = 'Travaux Pratiques (TP)'
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre


class RenduDevoir(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='rendus')
    td = models.ForeignKey(
        TravailDirige, on_delete=models.CASCADE, null=True, blank=True, related_name='rendus'
    )
    tp = models.ForeignKey(
        TravailPratique, on_delete=models.CASCADE, null=True, blank=True, related_name='rendus'
    )
    fichier = models.FileField('Fichier rendu', upload_to='rendus/')
    date_rendu = models.DateTimeField('Date de rendu', auto_now_add=True)
    note = models.DecimalField('Note', max_digits=5, decimal_places=2, null=True, blank=True)
    commentaire = models.TextField('Commentaire', blank=True)
    corrige_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rendus_corriges',
    )

    class Meta:
        verbose_name = 'Rendu de devoir'
        verbose_name_plural = 'Rendus de devoirs'
        ordering = ['-date_rendu']

    def __str__(self):
        devoir = self.td or self.tp
        return f'{self.etudiant} — {devoir}'

    def clean(self):
        if bool(self.td) == bool(self.tp):
            raise ValidationError('Un rendu doit être lié à un TD ou un TP, pas les deux ni aucun.')

    @property
    def devoir(self):
        return self.td or self.tp

    @property
    def type_devoir(self):
        return 'TD' if self.td_id else 'TP'
