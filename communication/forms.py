from django import forms

from .models import Annonce, Notification


class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['titre', 'contenu', 'priorite', 'publie']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'publie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['destinataire', 'titre', 'message', 'lien']
        widgets = {
            'destinataire': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'lien': forms.TextInput(attrs={'class': 'form-control'}),
        }
