from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import DocumentForm
from .models import DocumentBibliotheque
from django.db.models import ProtectedError


@login_required
def document_list(request):
    items = DocumentBibliotheque.objects.all()
    categorie = request.GET.get('categorie', '')
    q = request.GET.get('q', '')
    if categorie:
        items = items.filter(categorie=categorie)
    if q:
        items = items.filter(titre__icontains=q) | items.filter(auteur__icontains=q)
    return render(request, 'library/document_list.html', {'items': items, 'categorie': categorie, 'q': q})


@login_required
@role_required(User.Role.ADMIN, User.Role.TEACHER)
def document_create(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.ajoute_par = request.user
        doc.save()
        messages.success(request, 'Document ajouté.')
        return redirect('library:document_list')
    return render(request, 'library/form.html', {'form': form, 'title': 'Nouveau document', 'back_url': 'library:document_list'})


@login_required
@role_required(User.Role.ADMIN)
def document_delete(request, pk):
    obj = get_object_or_404(DocumentBibliotheque, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Document supprimé.')
            return redirect('library:document_list')
        except ProtectedError:
            messages.error(request, 'Impossible de supprimer ce document car il est lié à d\'autres enregistrements.')
            return redirect('library:document_list')
    return render(request, 'library/confirm_delete.html', {'object': obj, 'back_url': 'library:document_list'})


@login_required
def document_download(request, pk):
    obj = get_object_or_404(DocumentBibliotheque, pk=pk)
    if obj.fichier:
        return FileResponse(obj.fichier.open('rb'), as_attachment=True, filename=obj.fichier.name.split('/')[-1])
    messages.error(request, 'Aucun fichier disponible.')
    return redirect('library:document_list')
