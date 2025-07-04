# Arquivo: core/urls.py (versão final completa)

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # URLs Principais e de Perfil
    path('', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('selecionar-instituicao/', views.selecionar_instituicao_view, name='selecionar_instituicao'),

    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path(
        'perfil/alterar-senha/',
        auth_views.PasswordChangeView.as_view(
            template_name='perfil/alterar_senha.html',
            success_url=reverse_lazy('senha_alterada_sucesso')
        ),
        name='alterar_senha'
    ),
    path(
        'perfil/alterar-senha/sucesso/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='perfil/senha_alterada_sucesso.html'
        ),
        name='senha_alterada_sucesso'
    ),

    # URLs de Processo e sub-recursos
    path('processo/novo/', views.processo_create_view, name='processo_create'),
    path('processo/<int:pk>/', views.processo_detail_view, name='processo_detail'),
    path('processo/<int:pk>/editar/', views.processo_update_view, name='processo_update'),
    path('processo/<int:pk>/documentos/', views.ged_explorer_view, name='ged_explorer'),
    path('processo/<int:pk>/download-all/', views.download_all_documents_view, name='download_all_documents'),

    # URLs de itens específicos
    path('documento/<int:pk>/excluir/', views.documento_delete_view, name='documento_delete'),
    path('plano-acao/<int:pk>/editar/', views.plano_acao_update_view, name='plano_acao_update'),

    # URLs do Simulador
    path('processo/<int:pk>/simular/', views.simulador_view, name='simulador'),
    path('simulacao/<int:pk>/editar/', views.simulacao_update_view, name='simulacao_update'),
    path('simulacao/<int:pk>/resultado/', views.simulacao_resultado_view, name='simulacao_resultado'),

    # URLs da API
    path('api/processos-status/', views.processos_status_api_view, name='api_processos_status'),
    path('api/simulacao-eixos/', views.simulacao_eixos_api_view, name='api_simulacao_eixos'),
    path('api/notificacoes/marcar-como-lida/', views.marcar_notificacoes_como_lidas_api_view, name='api_marcar_como_lida'),
]