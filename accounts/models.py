from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        TEACHER = 'teacher', 'Enseignant'
        STUDENT = 'student', 'Étudiant'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    photo = models.ImageField('Photo', upload_to='photos/', blank=True, null=True)
    is_active_user = models.BooleanField('Compte actif', default=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class Activite(models.Model):
    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activites'
    )
    action = models.CharField('Action', max_length=255)
    module = models.CharField('Module', max_length=100)
    created_at = models.DateTimeField('Date', auto_now_add=True)

    class Meta:
        verbose_name = 'Activité'
        verbose_name_plural = 'Activités'
        ordering = ['-created_at']

    def __str__(self):
        return self.action
