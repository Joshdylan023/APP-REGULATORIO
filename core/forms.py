# Arquivo: core/forms.py

from django import forms
from .models import ProcessoRegulatorio, Documento, Perfil, PlanoDeAcao, Prazo, Pasta

class ProcessoForm(forms.ModelForm):
    class Meta:
        model = ProcessoRegulatorio
        fields = ['tipo_processo', 'curso', 'status', 'protocolo_mec', 'responsavel']
        widgets = {
            'tipo_processo': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'protocolo_mec': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'arquivo']

class PerfilFotoForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']

class PlanoDeAcaoForm(forms.ModelForm):
    class Meta:
        model = PlanoDeAcao
        fields = ['descricao', 'responsavel_acao', 'data_limite', 'status']
        widgets = {
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsavel_acao': forms.Select(attrs={'class': 'form-select'}),
            'data_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class PrazoForm(forms.ModelForm):
    class Meta:
        model = Prazo
        fields = ['descricao', 'data']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PastaForm(forms.ModelForm):
    class Meta:
        model = Pasta
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da nova pasta...'}),
        }