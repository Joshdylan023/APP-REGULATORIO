# Arquivo: core/middleware.py

from .models import Instituicao, Perfil, Notificacao # Verifique se Notificacao e Perfil estão importados
from django.utils.deprecation import MiddlewareMixin

class AppDataMiddleware(MiddlewareMixin):
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
                instituicoes_diretas = perfil.instituicoes.all()
                instituicoes_via_mantenedora = Instituicao.objects.filter(mantenedora__in=perfil.mantenedoras.all())
                # CORREÇÃO: Mude mantenedora.instituicao_set.all() para mantenedora.instituicoes.all()
                instituicoes_acessiveis = (instituicoes_diretas | instituicoes_via_mantenedora).distinct()
                
                request.instituicoes_acessiveis_usuario = instituicoes_acessiveis
                
                instituicao_ativa_id = request.session.get('instituicao_ativa_id')
                if instituicao_ativa_id:
                    # Tente obter a instituição ativa de dentro das instituições acessíveis
                    try:
                        request.instituicao_ativa = instituicoes_acessiveis.get(pk=instituicao_ativa_id)
                    except Instituicao.DoesNotExist:
                        request.instituicao_ativa = None
                        if 'instituicao_ativa_id' in request.session:
                            del request.session['instituicao_ativa_id'] # Limpa a sessão se a IES não for mais acessível
                
                # --- LÓGICA DAS NOTIFICAÇÕES ---
                notificacoes = Notificacao.objects.filter(usuario=request.user) # Já corrigido para 'usuario'
                request.notificacoes_nao_lidas_count = notificacoes.filter(lida=False).count()
                request.notificacoes_recentes = notificacoes.order_by('-data_criacao')[:5]

            except (Perfil.DoesNotExist, Instituicao.DoesNotExist):
                # Isso pode acontecer se o perfil ainda não existir ou a IES for deletada
                pass
        
        response = self.get_response(request)
        return response