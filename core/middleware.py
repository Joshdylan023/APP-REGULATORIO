# Ficheiro: core/middleware.py (Versão Final e Robusta)

from .models import Instituicao, Perfil, Notificacao

class AppDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define valores padrão
        request.instituicao_ativa = None
        request.instituicoes_acessiveis_usuario = []
        request.notificacoes_nao_lidas_count = 0
        request.notificacoes_recentes = []

        if request.user.is_authenticated:
            try:
                perfil, created = Perfil.objects.get_or_create(user=request.user)
                
                # --- Lógica das Instituições ---
                instituicoes_diretas_ids = set(perfil.instituicoes.values_list('pk', flat=True))
                instituicoes_via_mantenedora_ids = set(Instituicao.objects.filter(mantenedora__in=perfil.mantenedoras.all()).values_list('pk', flat=True))
                todos_ids = instituicoes_diretas_ids.union(instituicoes_via_mantenedora_ids)
                request.instituicoes_acessiveis_usuario = Instituicao.objects.filter(pk__in=todos_ids).order_by('nome')
                
                instituicao_ativa_id = request.session.get('instituicao_ativa_id')
                if instituicao_ativa_id:
                    request.instituicao_ativa = request.instituicoes_acessiveis_usuario.get(pk=instituicao_ativa_id)
                
                # --- LÓGICA DAS NOTIFICAÇÕES (Verifique esta parte) ---
                notificacoes = Notificacao.objects.filter(destinatario=request.user)
                request.notificacoes_nao_lidas_count = notificacoes.filter(lida=False).count()
                request.notificacoes_recentes = notificacoes.order_by('-data_criacao')[:5]

            except (Perfil.DoesNotExist, Instituicao.DoesNotExist):
                pass
        
        response = self.get_response(request)
        return response