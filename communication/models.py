from django.conf import settings
from django.db import models


class Annonce(models.Model):
    class Priorite(models.TextChoices):
        NORMALE = 'normale', 'Normale'
        IMPORTANTE = 'importante', 'Importante'
        URGENTE = 'urgente', 'Urgente'

    titre = models.CharField('Titre', max_length=300)
    contenu = models.TextField('Contenu')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='annonces')
    priorite = models.CharField('Priorité', max_length=20, choices=Priorite.choices, default=Priorite.NORMALE)
    publie = models.BooleanField('Publié', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces universitaires'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre


class Notification(models.Model):
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    titre = models.CharField('Titre', max_length=300)
    message = models.TextField('Message')
    lu = models.BooleanField('Lu', default=False)
    lien = models.CharField('Lien', max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre
