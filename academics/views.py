from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import log_activity, role_required
from accounts.models import User

from .forms import (
    DepartementForm, EnseignantForm, EtudiantForm, FaculteForm,
    FiliereForm, MatiereForm, NiveauEtudeForm,
)
from .models import Departement, Enseignant, Etudiant, Faculte, Filiere, Matiere, NiveauEtude


@login_required
@role_required(User.Role.ADMIN)
def faculte_list(request):
    items = Faculte.objects.all()
    return render(request, 'academics/faculte_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def faculte_create(request):
    form = FaculteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Création faculté', 'Facultés')
        messages.success(request, 'Faculté créée.')
        return redirect('academics:faculte_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Nouvelle faculté', 'back_url': 'academics:faculte_list'})


@login_required
@role_required(User.Role.ADMIN)
def faculte_edit(request, pk):
    obj = get_object_or_404(Faculte, pk=pk)
    form = FaculteForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Faculté modifiée.')
        return redirect('academics:faculte_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Modifier faculté', 'back_url': 'academics:faculte_list'})


@login_required
@role_required(User.Role.ADMIN)
def faculte_delete(request, pk):
    obj = get_object_or_404(Faculte, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Faculté supprimée.')
        return redirect('academics:faculte_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:faculte_list'})


@login_required
@role_required(User.Role.ADMIN)
def departement_list(request):
    items = Departement.objects.select_related('faculte').all()
    return render(request, 'academics/departement_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def departement_create(request):
    form = DepartementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Création département', 'Départements')
        messages.success(request, 'Département créé.')
        return redirect('academics:departement_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Nouveau département', 'back_url': 'academics:departement_list'})


@login_required
@role_required(User.Role.ADMIN)
def departement_edit(request, pk):
    obj = get_object_or_404(Departement, pk=pk)
    form = DepartementForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Département modifié.')
        return redirect('academics:departement_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Modifier département', 'back_url': 'academics:departement_list'})


@login_required
@role_required(User.Role.ADMIN)
def departement_delete(request, pk):
    obj = get_object_or_404(Departement, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Département supprimé.')
        return redirect('academics:departement_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:departement_list'})


@login_required
@role_required(User.Role.ADMIN)
def filiere_list(request):
    items = Filiere.objects.select_related('departement__faculte').all()
    return render(request, 'academics/filiere_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def filiere_create(request):
    form = FiliereForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Création filière', 'Filières')
        messages.success(request, 'Filière créée.')
        return redirect('academics:filiere_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Nouvelle filière', 'back_url': 'academics:filiere_list'})


@login_required
@role_required(User.Role.ADMIN)
def filiere_edit(request, pk):
    obj = get_object_or_404(Filiere, pk=pk)
    form = FiliereForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Filière modifiée.')
        return redirect('academics:filiere_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Modifier filière', 'back_url': 'academics:filiere_list'})


@login_required
@role_required(User.Role.ADMIN)
def filiere_delete(request, pk):
    obj = get_object_or_404(Filiere, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Filière supprimée.')
        return redirect('academics:filiere_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:filiere_list'})


@login_required
@role_required(User.Role.ADMIN)
def niveau_list(request):
    items = NiveauEtude.objects.all()
    return render(request, 'academics/niveau_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def niveau_create(request):
    form = NiveauEtudeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Niveau créé.')
        return redirect('academics:niveau_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Nouveau niveau', 'back_url': 'academics:niveau_list'})


@login_required
@role_required(User.Role.ADMIN)
def niveau_edit(request, pk):
    obj = get_object_or_404(NiveauEtude, pk=pk)
    form = NiveauEtudeForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Niveau modifié.')
        return redirect('academics:niveau_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Modifier niveau', 'back_url': 'academics:niveau_list'})


@login_required
@role_required(User.Role.ADMIN)
def niveau_delete(request, pk):
    obj = get_object_or_404(NiveauEtude, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Niveau supprimé.')
        return redirect('academics:niveau_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:niveau_list'})


@login_required
def matiere_list(request):
    items = Matiere.objects.select_related('filiere', 'niveau').all()
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        items = items.filter(enseignants=request.user.enseignant)
    return render(request, 'academics/matiere_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def matiere_create(request):
    form = MatiereForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Matière créée.')
        return redirect('academics:matiere_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Nouvelle matière', 'back_url': 'academics:matiere_list'})


@login_required
@role_required(User.Role.ADMIN)
def matiere_edit(request, pk):
    obj = get_object_or_404(Matiere, pk=pk)
    form = MatiereForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Matière modifiée.')
        return redirect('academics:matiere_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Modifier matière', 'back_url': 'academics:matiere_list'})


@login_required
@role_required(User.Role.ADMIN)
def matiere_delete(request, pk):
    obj = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Matière supprimée.')
        return redirect('academics:matiere_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:matiere_list'})


@login_required
@role_required(User.Role.ADMIN)
def enseignant_list(request):
    items = Enseignant.objects.select_related('user', 'departement').all()
    return render(request, 'academics/enseignant_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def enseignant_create(request):
    teachers = User.objects.filter(role=User.Role.TEACHER).exclude(enseignant__isnull=False)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        form = EnseignantForm(request.POST)
        if user_id and form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.user_id = user_id
            enseignant.save()
            form.save_m2m()
            messages.success(request, 'Enseignant créé.')
            return redirect('academics:enseignant_list')
    else:
        form = EnseignantForm()
    return render(request, 'academics/enseignant_form.html', {'form': form, 'teachers': teachers, 'title': 'Nouvel enseignant'})


@login_required
@role_required(User.Role.ADMIN)
def enseignant_edit(request, pk):
    obj = get_object_or_404(Enseignant, pk=pk)
    form = EnseignantForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Enseignant modifié.')
        return redirect('academics:enseignant_list')
    return render(request, 'academics/enseignant_form.html', {'form': form, 'teachers': [], 'title': 'Modifier enseignant', 'edit': True})


@login_required
@role_required(User.Role.ADMIN)
def enseignant_delete(request, pk):
    obj = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Enseignant supprimé.')
        return redirect('academics:enseignant_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:enseignant_list'})


@login_required
def etudiant_list(request):
    items = Etudiant.objects.select_related('user', 'filiere', 'niveau').all()
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        items = items.filter(filiere__matieres__in=request.user.enseignant.matieres.all()).distinct()
    elif request.user.is_student:
        items = items.filter(user=request.user)
    return render(request, 'academics/etudiant_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN)
def etudiant_create(request):
    students = User.objects.filter(role=User.Role.STUDENT).exclude(etudiant__isnull=False)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        form = EtudiantForm(request.POST)
        if user_id and form.is_valid():
            etudiant = form.save(commit=False)
            etudiant.user_id = user_id
            etudiant.save()
            messages.success(request, 'Étudiant créé.')
            return redirect('academics:etudiant_list')
    else:
        form = EtudiantForm()
    return render(request, 'academics/etudiant_form.html', {'form': form, 'students': students, 'title': 'Nouvel étudiant'})


@login_required
@role_required(User.Role.ADMIN)
def etudiant_edit(request, pk):
    obj = get_object_or_404(Etudiant, pk=pk)
    form = EtudiantForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Étudiant modifié.')
        return redirect('academics:etudiant_list')
    return render(request, 'academics/etudiant_form.html', {'form': form, 'students': [], 'title': 'Modifier étudiant', 'edit': True})


@login_required
@role_required(User.Role.ADMIN)
def etudiant_delete(request, pk):
    obj = get_object_or_404(Etudiant, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Étudiant supprimé.')
        return redirect('academics:etudiant_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'back_url': 'academics:etudiant_list'})
