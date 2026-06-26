from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import json

from accounts.decorators import log_activity, role_required
from accounts.forms import UserCreateForm, UserForm
from accounts.models import Activite, User
from academics.models import (
    Departement, Enseignant, Etudiant, Faculte, Filiere, Matiere, NiveauEtude,
)
from communication.models import Annonce
from pedagogy.models import Cours, RenduDevoir, TravailDirige, TravailPratique
from schedule.models import EmploiDuTemps


def login_view(request):
    from django.contrib.auth import login as auth_login
    from accounts.forms import LoginForm

    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not user.is_active_user:
            messages.error(request, 'Ce compte est désactivé. Contactez l\'administration.')
            return render(request, 'accounts/login.html', {'form': form})
        auth_login(request, user)
        log_activity(user, 'Connexion à la plateforme', 'Authentification')
        return redirect('accounts:dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/home.html')


def logout_view(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    return redirect('accounts:login')


@login_required
def dashboard(request):
    user = request.user
    current_year = timezone.now().year

    if user.is_admin:
        stats = {
            'etudiants': Etudiant.objects.count(),
            'enseignants': Enseignant.objects.count(),
            'facultes': Faculte.objects.count(),
            'departements': Departement.objects.count(),
            'cours': Cours.objects.count(),
            'tds': TravailDirige.objects.count(),
            'tps': TravailPratique.objects.count(),
            'rendus': RenduDevoir.objects.count(),
            'utilisateurs': User.objects.count(),
            'inscriptions_annee': Etudiant.objects.filter(annee_inscription=current_year).count(),
        }
        activites = Activite.objects.select_related('utilisateur')[:10]
        chart_faculte = list(
            Etudiant.objects.values('filiere__departement__faculte__nom')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        chart_inscriptions = list(
            Etudiant.objects.values('annee_inscription')
            .annotate(total=Count('id'))
            .order_by('annee_inscription')
        )
        annonces = Annonce.objects.filter(publie=True)[:5]
        return render(request, 'accounts/dashboard_admin.html', {
            'stats': stats,
            'activites': activites,
            'chart_faculte': json.dumps(chart_faculte),
            'chart_inscriptions': json.dumps(chart_inscriptions),
            'annonces': annonces,
        })

    if user.is_teacher:
        enseignant = getattr(user, 'enseignant', None)
        if enseignant:
            mes_cours = Cours.objects.filter(enseignant=enseignant).count()
            mes_tds = TravailDirige.objects.filter(enseignant=enseignant).count()
            mes_tps = TravailPratique.objects.filter(enseignant=enseignant).count()
            from django.db.models import Q
            rendus_en_attente = RenduDevoir.objects.filter(
                Q(td__enseignant=enseignant) | Q(tp__enseignant=enseignant),
                note__isnull=True,
            ).count()
            mes_etudiants = Etudiant.objects.filter(
                filiere__matieres__in=enseignant.matieres.all()
            ).distinct().count()
            moyenne_classe = RenduDevoir.objects.filter(
                Q(td__enseignant=enseignant) | Q(tp__enseignant=enseignant),
                note__isnull=False,
            ).aggregate(avg=Avg('note'))['avg'] or 0
        else:
            mes_cours = mes_tds = mes_tps = rendus_en_attente = mes_etudiants = 0
            moyenne_classe = 0
        return render(request, 'accounts/dashboard_teacher.html', {
            'enseignant': enseignant,
            'mes_cours': mes_cours,
            'mes_tds': mes_tds,
            'mes_tps': mes_tps,
            'rendus_en_attente': rendus_en_attente,
            'mes_etudiants': mes_etudiants,
            'moyenne_classe': round(float(moyenne_classe), 2),
            'annonces': Annonce.objects.filter(publie=True)[:5],
        })

    etudiant = getattr(user, 'etudiant', None)
    if etudiant:
        rendus = RenduDevoir.objects.filter(etudiant=etudiant).select_related('td', 'tp')
        notes_corrigees = rendus.filter(note__isnull=False)
        moyenne = notes_corrigees.aggregate(avg=Avg('note'))['avg'] or 0
        emploi = EmploiDuTemps.objects.filter(
            filiere=etudiant.filiere, niveau=etudiant.niveau
        ).select_related('matiere', 'enseignant')
    else:
        rendus = RenduDevoir.objects.none()
        moyenne = 0
        emploi = EmploiDuTemps.objects.none()
    return render(request, 'accounts/dashboard_student.html', {
        'etudiant': etudiant,
        'rendus': rendus[:5],
        'moyenne': round(float(moyenne), 2),
        'emploi': emploi[:5],
        'annonces': Annonce.objects.filter(publie=True)[:5],
    })


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
@role_required(User.Role.ADMIN)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    q = request.GET.get('q', '')
    role = request.GET.get('role', '')
    if q:
        users = users.filter(username__icontains=q) | users.filter(first_name__icontains=q) | users.filter(last_name__icontains=q)
    if role:
        users = users.filter(role=role)
    return render(request, 'accounts/user_list.html', {'users': users, 'q': q, 'role': role})


@login_required
@role_required(User.Role.ADMIN)
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_activity(request.user, f'Création utilisateur {user.username}', 'Utilisateurs')
            messages.success(request, 'Utilisateur créé avec succès.')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Nouvel utilisateur'})


@login_required
@role_required(User.Role.ADMIN)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            log_activity(request.user, f'Modification utilisateur {user.username}', 'Utilisateurs')
            messages.success(request, 'Utilisateur modifié avec succès.')
            return redirect('accounts:user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Modifier utilisateur'})


@login_required
@role_required(User.Role.ADMIN)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        else:
            username = user.username
            user.delete()
            log_activity(request.user, f'Suppression utilisateur {username}', 'Utilisateurs')
            messages.success(request, 'Utilisateur supprimé.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/confirm_delete.html', {'object': user, 'type': 'utilisateur'})


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


@login_required
def notification_mark_read(request, pk):
    notif = get_object_or_404(request.user.notifications, pk=pk)
    notif.lu = True
    notif.save()
    if notif.lien:
        return redirect(notif.lien)
    return redirect('accounts:notifications')


@login_required
def settings_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        if request.FILES.get('photo'):
            user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Paramètres mis à jour.')
        return redirect('accounts:settings')
    return render(request, 'accounts/settings.html')
