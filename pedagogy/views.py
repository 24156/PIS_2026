from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import log_activity, role_required
from accounts.models import User
from communication.models import Notification

from .forms import CorrectionForm, CoursForm, RenduForm, TDForm, TPForm
from .models import Cours, RenduDevoir, TravailDirige, TravailPratique


def _teacher_filter(qs, user):
    if user.is_teacher and hasattr(user, 'enseignant'):
        return qs.filter(enseignant=user.enseignant)
    return qs


def _student_matiere_filter(qs, user):
    if user.is_student and hasattr(user, 'etudiant'):
        et = user.etudiant
        return qs.filter(matiere__filiere=et.filiere, matiere__niveau=et.niveau)
    return qs


def _get_rendu_for_student(etudiant, td=None, tp=None):
    if td:
        return RenduDevoir.objects.filter(etudiant=etudiant, td=td).first()
    if tp:
        return RenduDevoir.objects.filter(etudiant=etudiant, tp=tp).first()
    return None


# --- Cours ---
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
        form.fields['enseignant'].initial = request.user.enseignant
        form.fields['enseignant'].queryset = form.fields['enseignant'].queryset.filter(pk=request.user.enseignant.pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_activity(request.user, 'Publication cours', 'Cours')
        messages.success(request, 'Cours publié.')
        return redirect('pedagogy:cours_list')
    return render(request, 'pedagogy/form.html', {'form': form, 'title': 'Nouveau cours', 'back_url': 'pedagogy:cours_list'})


@login_required
def cours_edit(request, pk):
    obj = get_object_or_404(Cours, pk=pk)
    if request.user.is_teacher and hasattr(request.user, 'enseignant') and obj.enseignant != request.user.enseignant:
        messages.error(request, 'Permission refusée.')
        return redirect('pedagogy:cours_list')
    form = CoursForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cours modifié.')
        return redirect('pedagogy:cours_list')
    return render(request, 'pedagogy/form.html', {'form': form, 'title': 'Modifier cours', 'back_url': 'pedagogy:cours_list'})


@login_required
def cours_delete(request, pk):
    obj = get_object_or_404(Cours, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Cours supprimé.')
        return redirect('pedagogy:cours_list')
    return render(request, 'pedagogy/confirm_delete.html', {'object': obj, 'back_url': 'pedagogy:cours_list'})


@login_required
def cours_download(request, pk):
    obj = get_object_or_404(Cours, pk=pk)
    if obj.fichier:
        return FileResponse(obj.fichier.open('rb'), as_attachment=True, filename=obj.fichier.name.split('/')[-1])
    messages.error(request, 'Aucun fichier disponible.')
    return redirect('pedagogy:cours_list')


# --- TD ---
@login_required
def td_list(request):
    items = TravailDirige.objects.select_related('matiere', 'enseignant__user').all()
    items = _teacher_filter(items, request.user)
    items = _student_matiere_filter(items, request.user)
    rendus_map = {}
    if request.user.is_student and hasattr(request.user, 'etudiant'):
        for r in RenduDevoir.objects.filter(etudiant=request.user.etudiant, td__in=items):
            rendus_map[r.td_id] = r
    return render(request, 'pedagogy/td_list.html', {
        'items': items,
        'rendus_map': rendus_map,
    })


@login_required
def td_create(request):
    if not (request.user.is_admin or request.user.is_teacher):
        return redirect('pedagogy:td_list')
    form = TDForm(request.POST or None, request.FILES or None)
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        form.fields['enseignant'].initial = request.user.enseignant
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'TD publié.')
        return redirect('pedagogy:td_list')
    return render(request, 'pedagogy/form.html', {'form': form, 'title': 'Nouveau TD', 'back_url': 'pedagogy:td_list'})


@login_required
def td_delete(request, pk):
    obj = get_object_or_404(TravailDirige, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('pedagogy:td_list')
    return render(request, 'pedagogy/confirm_delete.html', {'object': obj, 'back_url': 'pedagogy:td_list'})


# --- TP ---
@login_required
def tp_list(request):
    items = TravailPratique.objects.select_related('matiere', 'enseignant__user').all()
    items = _teacher_filter(items, request.user)
    items = _student_matiere_filter(items, request.user)
    rendus_map = {}
    if request.user.is_student and hasattr(request.user, 'etudiant'):
        for r in RenduDevoir.objects.filter(etudiant=request.user.etudiant, tp__in=items):
            rendus_map[r.tp_id] = r
    return render(request, 'pedagogy/tp_list.html', {
        'items': items,
        'rendus_map': rendus_map,
    })


@login_required
def tp_create(request):
    if not (request.user.is_admin or request.user.is_teacher):
        return redirect('pedagogy:tp_list')
    form = TPForm(request.POST or None, request.FILES or None)
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        form.fields['enseignant'].initial = request.user.enseignant
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'TP publié.')
        return redirect('pedagogy:tp_list')
    return render(request, 'pedagogy/form.html', {'form': form, 'title': 'Nouveau TP', 'back_url': 'pedagogy:tp_list'})


@login_required
def tp_delete(request, pk):
    obj = get_object_or_404(TravailPratique, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('pedagogy:tp_list')
    return render(request, 'pedagogy/confirm_delete.html', {'object': obj, 'back_url': 'pedagogy:tp_list'})


# --- TP/TD combiné (interface étudiant) ---
@login_required
def tp_td_list(request):
    tds = TravailDirige.objects.select_related('matiere', 'enseignant__user').all()
    tps = TravailPratique.objects.select_related('matiere', 'enseignant__user').all()
    tds = _teacher_filter(tds, request.user)
    tps = _teacher_filter(tps, request.user)
    tds = _student_matiere_filter(tds, request.user)
    tps = _student_matiere_filter(tps, request.user)

    rendus_td = {}
    rendus_tp = {}
    if request.user.is_student and hasattr(request.user, 'etudiant'):
        et = request.user.etudiant
        for r in RenduDevoir.objects.filter(etudiant=et, td__in=tds):
            rendus_td[r.td_id] = r
        for r in RenduDevoir.objects.filter(etudiant=et, tp__in=tps):
            rendus_tp[r.tp_id] = r

    td_items = [{'devoir': td, 'rendu': rendus_td.get(td.id)} for td in tds]
    tp_items = [{'devoir': tp, 'rendu': rendus_tp.get(tp.id)} for tp in tps]

    return render(request, 'pedagogy/tp_td_list.html', {
        'td_items': td_items,
        'tp_items': tp_items,
    })


# --- Rendu étudiant ---
@login_required
@role_required(User.Role.STUDENT)
def rendu_deposer_td(request, pk):
    td = get_object_or_404(TravailDirige, pk=pk)
    etudiant = request.user.etudiant
    existing = _get_rendu_for_student(etudiant, td=td)
    form = RenduForm(request.POST or None, request.FILES or None, instance=existing)
    if request.method == 'POST' and form.is_valid():
        rendu = form.save(commit=False)
        rendu.etudiant = etudiant
        rendu.td = td
        rendu.tp = None
        rendu.save()
        Notification.objects.create(
            destinataire=td.enseignant.user,
            titre='Nouveau rendu TD',
            message=f'{etudiant} a rendu le TD « {td.titre} ».',
            lien=reverse('pedagogy:rendu_list_td', kwargs={'pk': td.pk}),
        )
        messages.success(request, 'Votre travail a été envoyé.')
        return redirect('pedagogy:tp_td_list')
    return render(request, 'pedagogy/rendu_form.html', {
        'form': form,
        'devoir': td,
        'back_url': reverse('pedagogy:tp_td_list'),
    })


@login_required
@role_required(User.Role.STUDENT)
def rendu_deposer_tp(request, pk):
    tp = get_object_or_404(TravailPratique, pk=pk)
    etudiant = request.user.etudiant
    existing = _get_rendu_for_student(etudiant, tp=tp)
    form = RenduForm(request.POST or None, request.FILES or None, instance=existing)
    if request.method == 'POST' and form.is_valid():
        rendu = form.save(commit=False)
        rendu.etudiant = etudiant
        rendu.tp = tp
        rendu.td = None
        rendu.save()
        Notification.objects.create(
            destinataire=tp.enseignant.user,
            titre='Nouveau rendu TP',
            message=f'{etudiant} a rendu le TP « {tp.titre} ».',
            lien=reverse('pedagogy:rendu_list_tp', kwargs={'pk': tp.pk}),
        )
        messages.success(request, 'Votre travail a été envoyé.')
        return redirect('pedagogy:tp_td_list')
    return render(request, 'pedagogy/rendu_form.html', {
        'form': form,
        'devoir': tp,
        'back_url': reverse('pedagogy:tp_td_list'),
    })


# --- Rendus enseignant ---
@login_required
def rendu_list_td(request, pk):
    td = get_object_or_404(TravailDirige, pk=pk)
    if request.user.is_teacher and hasattr(request.user, 'enseignant') and td.enseignant != request.user.enseignant:
        messages.error(request, 'Accès refusé.')
        return redirect('pedagogy:td_list')
    rendus = RenduDevoir.objects.filter(td=td).select_related('etudiant__user')
    back_url = reverse('pedagogy:td_list')
    return render(request, 'pedagogy/rendu_list.html', {
        'devoir': td,
        'rendus': rendus,
        'back_url': back_url,
    })


@login_required
def rendu_list_tp(request, pk):
    tp = get_object_or_404(TravailPratique, pk=pk)
    if request.user.is_teacher and hasattr(request.user, 'enseignant') and tp.enseignant != request.user.enseignant:
        messages.error(request, 'Accès refusé.')
        return redirect('pedagogy:tp_list')
    rendus = RenduDevoir.objects.filter(tp=tp).select_related('etudiant__user')
    back_url = reverse('pedagogy:tp_list')
    return render(request, 'pedagogy/rendu_list.html', {
        'devoir': tp,
        'rendus': rendus,
        'back_url': back_url,
    })


@login_required
def rendu_download(request, pk):
    rendu = get_object_or_404(RenduDevoir, pk=pk)
    if request.user.is_student and hasattr(request.user, 'etudiant') and rendu.etudiant != request.user.etudiant:
        messages.error(request, 'Accès refusé.')
        return redirect('pedagogy:tp_td_list')
    if request.user.is_teacher and hasattr(request.user, 'enseignant'):
        devoir = rendu.devoir
        if devoir.enseignant != request.user.enseignant:
            messages.error(request, 'Accès refusé.')
            return redirect('pedagogy:td_list')
    return FileResponse(
        rendu.fichier.open('rb'),
        as_attachment=True,
        filename=rendu.fichier.name.split('/')[-1],
    )


@login_required
def rendu_corriger(request, pk):
    rendu = get_object_or_404(RenduDevoir.objects.select_related('td', 'tp', 'etudiant__user'), pk=pk)
    devoir = rendu.devoir
    if not (request.user.is_admin or (request.user.is_teacher and hasattr(request.user, 'enseignant') and devoir.enseignant == request.user.enseignant)):
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')

    if rendu.td_id:
        back_url = reverse('pedagogy:rendu_list_td', kwargs={'pk': rendu.td_id})
    else:
        back_url = reverse('pedagogy:rendu_list_tp', kwargs={'pk': rendu.tp_id})

    form = CorrectionForm(request.POST or None, instance=rendu)
    if request.method == 'POST' and form.is_valid():
        rendu = form.save(commit=False)
        rendu.corrige_par = request.user
        rendu.save()
        Notification.objects.create(
            destinataire=rendu.etudiant.user,
            titre='Note disponible',
            message=f'Votre {rendu.type_devoir} « {devoir.titre} » a été corrigé. Note : {rendu.note}/20.',
            lien=reverse('pedagogy:tp_td_list'),
        )
        log_activity(request.user, f'Correction rendu {rendu.etudiant}', 'TP/TD')
        messages.success(request, 'Note enregistrée.')
        return redirect(back_url)

    return render(request, 'pedagogy/rendu_correction.html', {
        'form': form,
        'rendu': rendu,
        'back_url': back_url,
    })
