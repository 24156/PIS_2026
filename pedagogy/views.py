from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import log_activity

from .forms import CoursForm, RenduForm, RenduGradeForm, TDForm, TPForm
from .models import Cours, Rendu, TravailDirige, TravailPratique
from django.db.models import ProtectedError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _teacher_filter(qs, user):
    """Filtre le queryset pour ne garder que les éléments de l'enseignant connecté."""
    if user.is_teacher and hasattr(user, 'enseignant'):
        return qs.filter(enseignant=user.enseignant)
    return qs


def _student_matiere_filter(qs, user):
    """Filtre le queryset pour ne garder que les matières de la filière/niveau de l'étudiant."""
    if user.is_student and hasattr(user, 'etudiant'):
        et = user.etudiant
        return qs.filter(matiere__filiere=et.filiere, matiere__niveau=et.niveau)
    return qs


def _can_manage(request, enseignant):
    if request.user.is_admin:
        return True
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        return enseignant == request.user.enseignant
    return False


def _student_can_access_devoir(user, devoir):
    if not user.is_student or not hasattr(user, 'etudiant'):
        return False
    et = user.etudiant
    return (
        devoir.matiere.filiere_id == et.filiere_id
        and devoir.matiere.niveau_id == et.niveau_id
    )


# ---------------------------------------------------------------------------
# Cours
# ---------------------------------------------------------------------------

@login_required
def cours_list(request):
    items = Cours.objects.select_related('matiere', 'enseignant__user').all()
    items = _teacher_filter(items, request.user)
    items = _student_matiere_filter(items, request.user)
    return render(request, 'pedagogy/cours_list.html', {'items': items})


@login_required
def cours_create(request):
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, 'Permission refusée.')
        return redirect('pedagogy:cours_list')
    form = CoursForm(request.POST or None, request.FILES or None)
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        from django import forms
        form.fields['enseignant'].initial = request.user.enseignant
        form.fields['enseignant'].widget = forms.HiddenInput()
        form.fields['matiere'].queryset = form.fields['matiere'].queryset.filter(
            enseignants=request.user.enseignant
        )
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Publication cours', 'Cours')
        messages.success(request, 'Cours publié.')
        return redirect('pedagogy:cours_list')
    return render(request, 'pedagogy/form.html', {
        'form': form, 'title': 'Nouveau cours', 'back_url': 'pedagogy:cours_list'
    })


@login_required
def cours_edit(request, pk):
    obj = get_object_or_404(Cours, pk=pk)
    if request.user.is_teacher and hasattr(request.user, 'enseignant') and obj.enseignant != request.user.enseignant:
        messages.error(request, 'Permission refusée.')
        return redirect('pedagogy:cours_list')
    form = CoursForm(request.POST or None, request.FILES or None, instance=obj)
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        from django import forms
        form.fields['enseignant'].initial = request.user.enseignant
        form.fields['enseignant'].widget = forms.HiddenInput()
        form.fields['matiere'].queryset = form.fields['matiere'].queryset.filter(
            enseignants=request.user.enseignant
        )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cours modifié.')
        return redirect('pedagogy:cours_list')
    return render(request, 'pedagogy/form.html', {
        'form': form, 'title': 'Modifier cours', 'back_url': 'pedagogy:cours_list'
    })


@login_required
def cours_delete(request, pk):
    obj = get_object_or_404(Cours, pk=pk)
    if not _can_manage(request, obj.enseignant):
        messages.error(request, 'Permission refusée.')
        return redirect('pedagogy:cours_list')
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Cours supprimé.')
            return redirect('pedagogy:cours_list')
        except ProtectedError:
            messages.error(request, 'Impossible de supprimer ce cours car il est lié à d\'autres enregistrements.')
            return redirect('pedagogy:cours_list')
    return render(request, 'pedagogy/confirm_delete.html', {
        'object': obj, 'back_url': 'pedagogy:cours_list'
    })


@login_required
def cours_download(request, pk):
    obj = get_object_or_404(Cours, pk=pk)
    if obj.fichier:
        return FileResponse(obj.fichier.open('rb'), as_attachment=True,
                            filename=obj.fichier.name.split('/')[-1])
    messages.error(request, 'Aucun fichier disponible.')
    return redirect('pedagogy:cours_list')


# ---------------------------------------------------------------------------
# TP / TD combinés (vue étudiant)
# ---------------------------------------------------------------------------

@login_required
def tp_td_list(request):
    """Liste combinée TP/TD avec statut de rendu et notes pour l'étudiant."""
    if not request.user.is_student or not hasattr(request.user, 'etudiant'):
        messages.error(request, 'Accès réservé aux étudiants.')
        return redirect('accounts:dashboard')

    etudiant = request.user.etudiant
    tds = TravailDirige.objects.select_related('matiere', 'enseignant__user').filter(
        matiere__filiere=etudiant.filiere,
        matiere__niveau=etudiant.niveau,
    )
    tps = TravailPratique.objects.select_related('matiere', 'enseignant__user').filter(
        matiere__filiere=etudiant.filiere,
        matiere__niveau=etudiant.niveau,
    )

    rendus = Rendu.objects.filter(etudiant=etudiant)
    rendus_by_td = {r.td_id: r for r in rendus if r.td_id}
    rendus_by_tp = {r.tp_id: r for r in rendus if r.tp_id}

    td_items = [{'devoir': td, 'rendu': rendus_by_td.get(td.pk)} for td in tds]
    tp_items = [{'devoir': tp, 'rendu': rendus_by_tp.get(tp.pk)} for tp in tps]

    return render(request, 'pedagogy/tp_td_list.html', {
        'td_items': td_items,
        'tp_items': tp_items,
        'now': timezone.now(),
    })


# ---------------------------------------------------------------------------
# TD
# ---------------------------------------------------------------------------

@login_required
def td_list(request):
    items = TravailDirige.objects.select_related('matiere', 'enseignant__user').all()
    items = _teacher_filter(items, request.user)
    items = _student_matiere_filter(items, request.user)

    # Attacher le rendu de l'étudiant à chaque TD pour affichage du statut
    if request.user.is_student and hasattr(request.user, 'etudiant'):
        etudiant = request.user.etudiant
        items = items.prefetch_related(
            Prefetch('rendus',
                     queryset=Rendu.objects.filter(etudiant=etudiant),
                     to_attr='_student_rendus')
        )
        items = list(items)
        for item in items:
            item.student_rendu = item._student_rendus[0] if item._student_rendus else None

    return render(request, 'pedagogy/td_list.html', {'items': items})


@login_required
def td_create(request):
    if not (request.user.is_admin or request.user.is_teacher):
        return redirect('pedagogy:td_list')
    form = TDForm(request.POST or None, request.FILES or None)
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        from django import forms
        form.fields['enseignant'].initial = request.user.enseignant
        form.fields['enseignant'].widget = forms.HiddenInput()
        form.fields['matiere'].queryset = form.fields['matiere'].queryset.filter(
            enseignants=request.user.enseignant
        )
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Publication TD', 'TD')
        messages.success(request, 'TD publié.')
        return redirect('pedagogy:td_list')
    return render(request, 'pedagogy/form.html', {
        'form': form, 'title': 'Nouveau TD', 'back_url': 'pedagogy:td_list'
    })


@login_required
def td_delete(request, pk):
    obj = get_object_or_404(TravailDirige, pk=pk)
    if not _can_manage(request, obj.enseignant):
        messages.error(request, 'Permission refusée.')
        return redirect('pedagogy:td_list')
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'TD supprimé.')
            return redirect('pedagogy:td_list')
        except ProtectedError:
            messages.error(request, 'Impossible de supprimer ce TD car il est lié à d\'autres enregistrements.')
            return redirect('pedagogy:td_list')
    return render(request, 'pedagogy/confirm_delete.html', {
        'object': obj, 'back_url': 'pedagogy:td_list'
    })


# ---------------------------------------------------------------------------
# TP
# ---------------------------------------------------------------------------

@login_required
def tp_list(request):
    items = TravailPratique.objects.select_related('matiere', 'enseignant__user').all()
    items = _teacher_filter(items, request.user)
    items = _student_matiere_filter(items, request.user)

    # Attacher le rendu de l'étudiant à chaque TP pour affichage du statut
    if request.user.is_student and hasattr(request.user, 'etudiant'):
        etudiant = request.user.etudiant
        items = items.prefetch_related(
            Prefetch('rendus',
                     queryset=Rendu.objects.filter(etudiant=etudiant),
                     to_attr='_student_rendus')
        )
        items = list(items)
        for item in items:
            item.student_rendu = item._student_rendus[0] if item._student_rendus else None

    return render(request, 'pedagogy/tp_list.html', {'items': items})


@login_required
def tp_create(request):
    if not (request.user.is_admin or request.user.is_teacher):
        return redirect('pedagogy:tp_list')
    form = TPForm(request.POST or None, request.FILES or None)
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        from django import forms
        form.fields['enseignant'].initial = request.user.enseignant
        form.fields['enseignant'].widget = forms.HiddenInput()
        form.fields['matiere'].queryset = form.fields['matiere'].queryset.filter(
            enseignants=request.user.enseignant
        )
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Publication TP', 'TP')
        messages.success(request, 'TP publié.')
        return redirect('pedagogy:tp_list')
    return render(request, 'pedagogy/form.html', {
        'form': form, 'title': 'Nouveau TP', 'back_url': 'pedagogy:tp_list'
    })


@login_required
def tp_delete(request, pk):
    obj = get_object_or_404(TravailPratique, pk=pk)
    if not _can_manage(request, obj.enseignant):
        messages.error(request, 'Permission refusée.')
        return redirect('pedagogy:tp_list')
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'TP supprimé.')
            return redirect('pedagogy:tp_list')
        except ProtectedError:
            messages.error(request, 'Impossible de supprimer ce TP car il est lié à d\'autres enregistrements.')
            return redirect('pedagogy:tp_list')
    return render(request, 'pedagogy/confirm_delete.html', {
        'object': obj, 'back_url': 'pedagogy:tp_list'
    })


# ---------------------------------------------------------------------------
# Dépôt de travail par l'étudiant (td_submit / tp_submit)
# ---------------------------------------------------------------------------

@login_required
def td_submit(request, pk):
    """L'étudiant dépose son fichier TD."""
    devoir = get_object_or_404(TravailDirige.objects.select_related('matiere'), pk=pk)

    if not request.user.is_student or not hasattr(request.user, 'etudiant'):
        messages.error(request, "Seuls les étudiants peuvent déposer un travail.")
        return redirect('pedagogy:td_list')

    if not _student_can_access_devoir(request.user, devoir):
        messages.error(request, "Ce devoir n'est pas disponible pour votre filière ou niveau.")
        return redirect('pedagogy:td_list')

    etudiant = request.user.etudiant
    # Récupérer le rendu existant ou en créer un nouveau (sans fichier encore)
    rendu = Rendu.objects.filter(etudiant=etudiant, td=devoir).first()

    if rendu and rendu.note is not None:
        messages.warning(request, "Ce travail a déjà été noté. Vous ne pouvez plus le modifier.")
        return redirect('pedagogy:td_list')

    if devoir.date_fin and timezone.now() > devoir.date_fin:
        messages.error(request, "La date limite pour ce travail est dépassée.")
        return redirect('pedagogy:td_list')

    form = RenduForm(request.POST or None, request.FILES or None, instance=rendu)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.etudiant = etudiant
        obj.td = devoir
        obj.tp = None
        obj.matiere = devoir.matiere
        obj.save()
        log_activity(request.user, f"Dépôt TD : {devoir.titre}", "TD")
        messages.success(request, "Votre travail a été déposé avec succès !")
        return redirect('pedagogy:td_list')

    return render(request, 'pedagogy/rendu_form.html', {
        'form': form,
        'devoir': devoir,
        'back_url': '/pedagogy/td/',
    })


@login_required
def tp_submit(request, pk):
    """L'étudiant dépose son fichier TP."""
    devoir = get_object_or_404(TravailPratique.objects.select_related('matiere'), pk=pk)

    if not request.user.is_student or not hasattr(request.user, 'etudiant'):
        messages.error(request, "Seuls les étudiants peuvent déposer un travail.")
        return redirect('pedagogy:tp_list')

    if not _student_can_access_devoir(request.user, devoir):
        messages.error(request, "Ce devoir n'est pas disponible pour votre filière ou niveau.")
        return redirect('pedagogy:tp_list')

    etudiant = request.user.etudiant
    rendu = Rendu.objects.filter(etudiant=etudiant, tp=devoir).first()

    if rendu and rendu.note is not None:
        messages.warning(request, "Ce travail a déjà été noté. Vous ne pouvez plus le modifier.")
        return redirect('pedagogy:tp_list')

    if devoir.date_fin and timezone.now() > devoir.date_fin:
        messages.error(request, "La date limite pour ce travail est dépassée.")
        return redirect('pedagogy:tp_list')

    form = RenduForm(request.POST or None, request.FILES or None, instance=rendu)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.etudiant = etudiant
        obj.tp = devoir
        obj.td = None
        obj.matiere = devoir.matiere
        obj.save()
        log_activity(request.user, f"Dépôt TP : {devoir.titre}", "TP")
        messages.success(request, "Votre travail a été déposé avec succès !")
        return redirect('pedagogy:tp_list')

    return render(request, 'pedagogy/rendu_form.html', {
        'form': form,
        'devoir': devoir,
        'back_url': '/pedagogy/tp/',
    })


# ---------------------------------------------------------------------------
# Vue des rendus pour l'enseignant
# ---------------------------------------------------------------------------

@login_required
def td_rendus(request, pk):
    """L'enseignant voit la liste des rendus pour son TD."""
    devoir = get_object_or_404(TravailDirige, pk=pk)

    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, "Accès refusé.")
        return redirect('pedagogy:td_list')

    # L'enseignant ne peut accéder qu'à ses propres devoirs
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        if devoir.enseignant != request.user.enseignant:
            messages.error(request, "Vous n'avez pas accès aux rendus de ce devoir.")
            return redirect('pedagogy:td_list')

    rendus = Rendu.objects.filter(td=devoir).select_related('etudiant__user', 'etudiant')
    return render(request, 'pedagogy/rendu_list.html', {
        'devoir': devoir,
        'rendus': rendus,
        'back_url': '/pedagogy/td/',
    })


@login_required
def tp_rendus(request, pk):
    """L'enseignant voit la liste des rendus pour son TP."""
    devoir = get_object_or_404(TravailPratique, pk=pk)

    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, "Accès refusé.")
        return redirect('pedagogy:tp_list')

    # L'enseignant ne peut accéder qu'à ses propres devoirs
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        if devoir.enseignant != request.user.enseignant:
            messages.error(request, "Vous n'avez pas accès aux rendus de ce devoir.")
            return redirect('pedagogy:tp_list')

    rendus = Rendu.objects.filter(tp=devoir).select_related('etudiant__user', 'etudiant')
    return render(request, 'pedagogy/rendu_list.html', {
        'devoir': devoir,
        'rendus': rendus,
        'back_url': '/pedagogy/tp/',
    })


# ---------------------------------------------------------------------------
# Correction / notation
# ---------------------------------------------------------------------------

@login_required
def rendu_corriger(request, pk):
    """L'enseignant note un rendu et laisse un commentaire."""
    rendu = get_object_or_404(
        Rendu.objects.select_related('td', 'tp', 'etudiant__user', 'etudiant'),
        pk=pk
    )

    # Déterminer le devoir associé
    devoir = rendu.td or rendu.tp
    if not devoir:
        messages.error(request, "Rendu invalide.")
        return redirect('accounts:dashboard')

    # Vérification des droits
    if not request.user.is_admin:
        if not (request.user.is_teacher and hasattr(request.user, 'enseignant')):
            messages.error(request, "Accès refusé.")
            return redirect('accounts:dashboard')
        if devoir.enseignant != request.user.enseignant:
            messages.error(request, "Accès refusé.")
            return redirect('accounts:dashboard')

    # URL de retour
    if rendu.td:
        back_url = f'/pedagogy/td/{rendu.td.pk}/rendus/'
    else:
        back_url = f'/pedagogy/tp/{rendu.tp.pk}/rendus/'

    form = RenduGradeForm(request.POST or None, instance=rendu)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if hasattr(request.user, 'enseignant'):
            obj.corrige_par = request.user.enseignant
        obj.date_correction = timezone.now()
        obj.save()
        log_activity(request.user, f"Correction de {rendu.etudiant}", "Notes")
        messages.success(request, f"Note {obj.note}/20 enregistrée pour {rendu.etudiant}.")
        return redirect(back_url)

    return render(request, 'pedagogy/rendu_correction.html', {
        'form': form,
        'rendu': rendu,
        'back_url': back_url,
    })


# ---------------------------------------------------------------------------
# Téléchargement du fichier rendu
# ---------------------------------------------------------------------------

@login_required
def rendu_download(request, pk):
    """Téléchargement du fichier déposé par l'étudiant."""
    rendu = get_object_or_404(Rendu, pk=pk)

    # Vérification des droits d'accès
    authorized = False
    if request.user.is_admin:
        authorized = True
    elif request.user.is_student and hasattr(request.user, 'etudiant'):
        if rendu.etudiant == request.user.etudiant:
            authorized = True
    elif request.user.is_teacher and hasattr(request.user, 'enseignant'):
        devoir = rendu.td or rendu.tp
        if devoir and devoir.enseignant == request.user.enseignant:
            authorized = True

    if not authorized:
        messages.error(request, "Accès refusé.")
        return redirect('accounts:dashboard')

    if rendu.fichier:
        return FileResponse(
            rendu.fichier.open('rb'),
            as_attachment=True,
            filename=rendu.fichier.name.split('/')[-1]
        )

    messages.error(request, "Aucun fichier disponible pour ce rendu.")
    return redirect('accounts:dashboard')
