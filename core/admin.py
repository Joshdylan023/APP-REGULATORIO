# Arquivo: core/admin.py

from django.contrib import admin
from .models import (
    Mantenedora, Instituicao, Perfil, Curso,
    ProcessoRegulatorio, Documento, Eixo, Indicador,
    Simulacao, NotaSimulada, Notificacao, PlanoDeAcao, Prazo, Pasta,
    LogAtividade
)

class PerfilAdmin(admin.ModelAdmin):
    filter_horizontal = ('mantenedoras', 'instituicoes',)

admin.site.register(Mantenedora)
admin.site.register(Instituicao)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Curso)
admin.site.register(ProcessoRegulatorio)
admin.site.register(Documento)
admin.site.register(Eixo)
admin.site.register(Indicador)
admin.site.register(Simulacao)
admin.site.register(NotaSimulada)
admin.site.register(Notificacao)
admin.site.register(PlanoDeAcao)
admin.site.register(Prazo)
admin.site.register(Pasta)
admin.site.register(LogAtividade)