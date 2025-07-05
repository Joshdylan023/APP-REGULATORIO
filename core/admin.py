# Arquivo: core/admin.py

from django.contrib import admin
from .models import (
    Mantenedora, Instituicao, Perfil, Curso,
    ProcessoRegulatorio, Documento, Eixo, Indicador,
    Simulacao, NotaSimulada, Notificacao, PlanoDeAcao, Prazo, Pasta,
    LogAtividade,
    InstrumentoAvaliacao, TipoProcesso # Já deve estar aqui após a alteração anterior
)

class PerfilAdmin(admin.ModelAdmin):
    filter_horizontal = ('mantenedoras', 'instituicoes',)

# NOVO CÓDIGO: Classe Admin para Notificacao
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('mensagem', 'usuario', 'lida', 'data_criacao', 'link') # Use 'usuario' ao invés de 'destinatario'
    list_filter = ('lida', 'data_criacao')
    search_fields = ('mensagem', 'usuario__username') # Permite buscar por mensagem ou nome de usuário
    ordering = ('-data_criacao',) # Ordena pelas notificações mais recentes

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
# Modifique o registro de Notificacao para usar a nova classe Admin
admin.site.register(Notificacao, NotificacaoAdmin) # <-- Mude esta linha
admin.site.register(PlanoDeAcao)
admin.site.register(Prazo)
admin.site.register(Pasta)
admin.site.register(LogAtividade)
admin.site.register(InstrumentoAvaliacao) # Deve estar 
admin.site.register(TipoProcesso)