from django import forms

from .models import DocumentBibliotheque


class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentBibliotheque
        fields = ['titre', 'auteur', 'categorie', 'description', 'fichier', 'isbn', 'annee_publication']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'auteur': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'annee_publication': forms.NumberInput(attrs={'class': 'form-control'}),
        }
