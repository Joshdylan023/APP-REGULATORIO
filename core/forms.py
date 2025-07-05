from django import forms
# Garanta que todos estes modelos estão importados, especialmente InstrumentoAvaliacao
from .models import ProcessoRegulatorio, Documento, Perfil, PlanoDeAcao, Prazo, Pasta, TipoProcesso, Curso, InstrumentoAvaliacao 

class ProcessoForm(forms.ModelForm):
    class Meta:
        model = ProcessoRegulatorio
        fields = [
            'nome',
            'descricao',
            'instituicao',
            'tipo',
            'instrumento_avaliacao',
            'curso',                  # <-- ESTA LINHA
            'data_protocolo',         # <-- E ESTA LINHA DEVEM ESTAR SEPARADAS
            'data_conclusao_prevista',
            'data_conclusao_real',
            'status',
            'responsavel'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instituicao': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'instrumento_avaliacao': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'data_protocolo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_conclusao_prevista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_conclusao_real': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nome_documento', 'arquivo'] # 'titulo' foi alterado para 'nome_documento'
        widgets = {
            'nome_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PerfilFotoForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']

class PlanoDeAcaoForm(forms.ModelForm):
    class Meta:
        model = PlanoDeAcao
        fields = ['titulo', 'descricao', 'responsavel', 'data_limite', 'status'] # <-- Adicionado 'titulo', 'responsavel_acao' alterado para 'responsavel'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}), # <-- NOVO: Widget para 'titulo'
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}), # <-- 'responsavel_acao' alterado para 'responsavel'
            'data_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class PrazoForm(forms.ModelForm):
    class Meta:
        model = Prazo
        fields = ['descricao', 'data_limite', 'concluido'] # Campos atualizados
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'data_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'concluido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PastaForm(forms.ModelForm):
    class Meta:
        model = Pasta
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da nova pasta...'}),
        }