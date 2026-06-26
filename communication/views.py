from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import log_activity, role_required
from accounts.models import User

from .forms import AnnonceForm, NotificationForm
from .models import Annonce, Notification


@login_required
def annonce_list(request):
    if request.user.is_admin:
        items = Annonce.objects.select_related('auteur').all()
    else:
        items = Annonce.objects.filter(publie=True).select_related('auteur')
    return render(request, 'communication/annonce_list.html', {'items': items})


@login_required
@role_required(User.Role.ADMIN, User.Role.TEACHER)
def annonce_create(request):
    form = AnnonceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        annonce = form.save(commit=False)
        annonce.auteur = request.user
        annonce.save()
        log_activity(request.user, 'Publication annonce', 'Annonces')
        messages.success(request, 'Annonce publiée.')
        return redirect('communication:annonce_list')
    return render(request, 'communication/form.html', {'form': form, 'title': 'Nouvelle annonce', 'back_url': 'communication:annonce_list'})


@login_required
@role_required(User.Role.ADMIN, User.Role.TEACHER)
def annonce_edit(request, pk):
    obj = get_object_or_404(Annonce, pk=pk)
    form = AnnonceForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Annonce modifiée.')
        return redirect('communication:annonce_list')
    return render(request, 'communication/form.html', {'form': form, 'title': 'Modifier annonce', 'back_url': 'communication:annonce_list'})


@login_required
@role_required(User.Role.ADMIN)
def annonce_delete(request, pk):
    obj = get_object_or_404(Annonce, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('communication:annonce_list')
    return render(request, 'communication/confirm_delete.html', {'object': obj, 'back_url': 'communication:annonce_list'})


@login_required
@role_required(User.Role.ADMIN)
def notification_send(request):
    form = NotificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Notification envoyée.')
        return redirect('communication:annonce_list')
    return render(request, 'communication/form.html', {'form': form, 'title': 'Envoyer notification', 'back_url': 'communication:annonce_list'})
