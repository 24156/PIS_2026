from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import EmploiDuTempsForm
from .models import EmploiDuTemps


@login_required
def emploi_list(request):
    items = EmploiDuTemps.objects.select_related('matiere', 'enseignant__user', 'filiere', 'niveau').all()
    if request.user.is_student and hasattr(request.user, 'etudiant'):
        et = request.user.etudiant
        items = items.filter(filiere=et.filiere, niveau=et.niveau)
    elif request.user.is_teacher and hasattr(request.user, 'enseignant'):
        items = items.filter(enseignant=request.user.enseignant)
    jours = EmploiDuTemps.Jour.choices
    emploi_grouped = [(label, items.filter(jour=code)) for code, label in jours]
    return render(request, 'schedule/emploi_list.html', {
        'items': items,
        'emploi_grouped': emploi_grouped,
        'jours': jours,
    })


@login_required
@role_required(User.Role.ADMIN)
def emploi_create(request):
    form = EmploiDuTempsForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Créneau ajouté.')
        return redirect('schedule:emploi_list')
    return render(request, 'schedule/form.html', {'form': form, 'title': 'Nouveau créneau', 'back_url': 'schedule:emploi_list'})


@login_required
@role_required(User.Role.ADMIN)
def emploi_edit(request, pk):
    obj = get_object_or_404(EmploiDuTemps, pk=pk)
    form = EmploiDuTempsForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Créneau modifié.')
        return redirect('schedule:emploi_list')
    return render(request, 'schedule/form.html', {'form': form, 'title': 'Modifier créneau', 'back_url': 'schedule:emploi_list'})


@login_required
@role_required(User.Role.ADMIN)
def emploi_delete(request, pk):
    obj = get_object_or_404(EmploiDuTemps, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('schedule:emploi_list')
    return render(request, 'schedule/confirm_delete.html', {'object': obj, 'back_url': 'schedule:emploi_list'})
