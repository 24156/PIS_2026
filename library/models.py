from django.conf import settings
from django.db import models


class DocumentBibliotheque(models.Model):
    class Categorie(models.TextChoices):
        LIVRE = 'livre', 'Livre'
        ARTICLE = 'article', 'Article'
        THESE = 'these', 'Thèse'
        MEMOIRE = 'memoire', 'Mémoire'
        RAPPORT = 'rapport', 'Rapport'
        AUTRE = 'autre', 'Autre'

    titre = models.CharField('Titre', max_length=300)
    auteur = models.CharField('Auteur', max_length=200)
    categorie = models.CharField('Catégorie', max_length=20, choices=Categorie.choices)
    description = models.TextField('Description', blank=True)
    fichier = models.FileField('Fichier', upload_to='bibliotheque/', blank=True, null=True)
    isbn = models.CharField('ISBN', max_length=50, blank=True)
    annee_publication = models.PositiveIntegerField('Année de publication', null=True, blank=True)
    ajoute_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='documents_ajoutes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Document bibliothèque'
        verbose_name_plural = 'Bibliothèque numérique'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre
