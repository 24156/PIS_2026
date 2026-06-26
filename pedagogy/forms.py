from django import forms

from .models import Cours, RenduDevoir, TravailDirige, TravailPratique


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
        fields = ['titre', 'matiere', 'enseignant', 'fichier', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'enseignant': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TPForm(forms.ModelForm):
    class Meta:
        model = TravailPratique
        fields = ['titre', 'matiere', 'enseignant', 'fichier', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'enseignant': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RenduForm(forms.ModelForm):
    class Meta:
        model = RenduDevoir
        fields = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CorrectionForm(forms.ModelForm):
    class Meta:
        model = RenduDevoir
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 20, 'step': 0.25}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
