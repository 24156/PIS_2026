from django.conf import settings
from django.db import models


class Faculte(models.Model):
    nom = models.CharField('Nom', max_length=200, unique=True)
    code = models.CharField('Code', max_length=20, unique=True)
    description = models.TextField('Description', blank=True)
    dean = models.CharField('Doyen', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Faculté'
        verbose_name_plural = 'Facultés'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Departement(models.Model):
    nom = models.CharField('Nom', max_length=200)
    code = models.CharField('Code', max_length=20, unique=True)
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE, related_name='departements')
    chef = models.CharField('Chef de département', max_length=200, blank=True)
    description = models.TextField('Description', blank=True)

    class Meta:
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'
        ordering = ['nom']

    def __str__(self):
        return f'{self.nom} ({self.faculte.code})'


class Filiere(models.Model):
    nom = models.CharField('Nom', max_length=200)
    code = models.CharField('Code', max_length=20, unique=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='filieres')
    description = models.TextField('Description', blank=True)
    duree_annees = models.PositiveIntegerField('Durée (années)', default=3)

    class Meta:
        verbose_name = 'Filière'
        verbose_name_plural = 'Filières'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class NiveauEtude(models.Model):
    class Niveau(models.TextChoices):
        L1 = 'L1', 'Licence 1'
        L2 = 'L2', 'Licence 2'
        L3 = 'L3', 'Licence 3'
        M1 = 'M1', 'Master 1'
        M2 = 'M2', 'Master 2'

    code = models.CharField('Code', max_length=5, choices=Niveau.choices, unique=True)
    description = models.CharField('Description', max_length=200, blank=True)

    class Meta:
        verbose_name = "Niveau d'études"
        verbose_name_plural = "Niveaux d'études"
        ordering = ['code']

    def __str__(self):
        return self.get_code_display()


class Matiere(models.Model):
    nom = models.CharField('Nom', max_length=200)
    code = models.CharField('Code', max_length=20, unique=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='matieres')
    niveau = models.ForeignKey(NiveauEtude, on_delete=models.CASCADE, related_name='matieres')
    coefficient = models.DecimalField('Coefficient', max_digits=4, decimal_places=2, default=1.0)
    credits = models.PositiveIntegerField('Crédits', default=3)
    description = models.TextField('Description', blank=True)

    class Meta:
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['nom']

    def __str__(self):
        return f'{self.code} - {self.nom}'


class Enseignant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enseignant')
    matricule = models.CharField('Matricule', max_length=30, unique=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, related_name='enseignants')
    grade = models.CharField('Grade', max_length=100, blank=True)
    specialite = models.CharField('Spécialité', max_length=200, blank=True)
    matieres = models.ManyToManyField(Matiere, blank=True, related_name='enseignants')

    class Meta:
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Etudiant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='etudiant')
    matricule = models.CharField('Matricule', max_length=30, unique=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.PROTECT, related_name='etudiants')
    niveau = models.ForeignKey(NiveauEtude, on_delete=models.PROTECT, related_name='etudiants')
    annee_inscription = models.PositiveIntegerField("Année d'inscription")
    date_naissance = models.DateField('Date de naissance', null=True, blank=True)
    lieu_naissance = models.CharField('Lieu de naissance', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def faculte(self):
        return self.filiere.departement.faculte
