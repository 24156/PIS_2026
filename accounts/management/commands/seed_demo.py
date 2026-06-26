from datetime import date, time

from django.core.management.base import BaseCommand

from accounts.models import User
from academics.models import Departement, Enseignant, Etudiant, Faculte, Filiere, Matiere, NiveauEtude
from communication.models import Annonce
from pedagogy.models import Cours, TravailDirige, TravailPratique
from schedule.models import EmploiDuTemps


class Command(BaseCommand):
    help = 'Initialise des données de démonstration'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write('Données déjà présentes, seed ignoré.')
            return

        admin = User.objects.create_superuser('admin', 'admin@pis.mr', 'admin123')
        admin.first_name = 'Admin'
        admin.last_name = 'Système'
        admin.role = User.Role.ADMIN
        admin.save()
        prof_user = User.objects.create_user('prof.mahmoud', password='prof123', role=User.Role.TEACHER, first_name='Mahmoud', last_name='Ba')
        etu_user = User.objects.create_user('etudiant.ahmed', password='etud123', role=User.Role.STUDENT, first_name='Ahmed', last_name='Mohamed')

        fac = Faculte.objects.create(nom='Faculté des Sciences', code='FS', dean='Dr. Sy')
        dep = Departement.objects.create(nom='Informatique', code='INFO', faculte=fac, chef='Prof. Ba')
        fil = Filiere.objects.create(nom='Licence Informatique', code='LINFO', departement=dep)
        n1 = NiveauEtude.objects.create(code='L1', description='Licence 1')
        mat = Matiere.objects.create(nom='Algorithmique', code='ALGO101', filiere=fil, niveau=n1)

        enseignant = Enseignant.objects.create(user=prof_user, matricule='ENS001', departement=dep, grade='Maître Assistant')
        enseignant.matieres.add(mat)

        etudiant = Etudiant.objects.create(
            user=etu_user, matricule='ETU23001', filiere=fil, niveau=n1, annee_inscription=2025
        )

        Cours.objects.create(titre='Introduction à l\'algorithmique', matiere=mat, enseignant=enseignant, description='Cours magistral S1')
        TravailDirige.objects.create(titre='TD1 - Complexité', matiere=mat, enseignant=enseignant, description='Analyse de complexité')
        TravailPratique.objects.create(titre='TP1 - Python', matiere=mat, enseignant=enseignant, description='Implémentation en Python')

        EmploiDuTemps.objects.create(
            matiere=mat, enseignant=enseignant, filiere=fil, niveau=n1,
            jour='lundi', heure_debut=time(8, 0), heure_fin=time(10, 0), salle='A101'
        )

        Annonce.objects.create(
            titre='Bienvenue sur PIS Mauritanie',
            contenu='La plateforme pédagogique est opérationnelle.',
            auteur=admin,
        )

        self.stdout.write(self.style.SUCCESS('Données de démonstration créées.'))
