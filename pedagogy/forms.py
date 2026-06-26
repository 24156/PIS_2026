from django import forms

from .models import Cours, Rendu, TravailDirige, TravailPratique


class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['titre', 'matiere', 'enseignant', 'fichier', 'description', 'annee_academique']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'enseignant': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'annee_academique': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TDForm(forms.ModelForm):
    class Meta:
        model = TravailDirige
        fields = ['titre', 'matiere', 'enseignant', 'fichier', 'description', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'enseignant': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class TPForm(forms.ModelForm):
    class Meta:
        model = TravailPratique
        fields = ['titre', 'matiere', 'enseignant', 'fichier', 'description', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'enseignant': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class RenduForm(forms.ModelForm):
    """Formulaire pour l'étudiant : dépôt du fichier travail."""
    class Meta:
        model = Rendu
        fields = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RenduGradeForm(forms.ModelForm):
    """Formulaire pour l'enseignant : saisie de la note et commentaire."""
    class Meta:
        model = Rendu
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 20,
                'step': 0.25,
                'placeholder': 'Note sur 20'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaires de correction...'
            }),
        }

    def clean_note(self):
        note = self.cleaned_data.get('note')
        if note is not None and (note < 0 or note > 20):
            raise forms.ValidationError('La note doit être comprise entre 0 et 20.')
        return note
