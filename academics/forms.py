from django import forms

from .models import (
    Departement, Enseignant, Etudiant, Faculte, Filiere, Matiere, NiveauEtude,
)


class FaculteForm(forms.ModelForm):
    class Meta:
        model = Faculte
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dean': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DepartementForm(forms.ModelForm):
    class Meta:
        model = Departement
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'faculte': forms.Select(attrs={'class': 'form-select'}),
            'chef': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FiliereForm(forms.ModelForm):
    class Meta:
        model = Filiere
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duree_annees': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class NiveauEtudeForm(forms.ModelForm):
    class Meta:
        model = NiveauEtude
        fields = '__all__'
        widgets = {
            'code': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = ['matricule', 'departement', 'grade', 'specialite', 'matieres']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
            'matieres': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['matricule', 'filiere', 'niveau', 'annee_inscription', 'date_naissance', 'lieu_naissance']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'annee_inscription': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
        }
