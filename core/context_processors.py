# Ficheiro: core/context_processors.py (versão corrigida para o NotSupportedError)

from .models import Instituicao, Perfil, Notificacao

def unified_context(request):
    if not request.user.is_authenticated:
        return {}

    context = {
        'notificacoes_nao_lidas_count': 0,
        'notificacoes_recentes': [],
        'instituicoes_acessiveis_usuario': [],
        'instituicao_ativa': None,
    }

    try:
        perfil, created = Perfil.objects.get_or_create(user=request.user)

        # --- LÓGICA CORRIGIDA DAS INSTITUIÇÕES ACESSÍVEIS ---
        # Pega os IDs de todas as instituições para evitar problemas de união
        instituicoes_diretas_ids = set(perfil.instituicoes.values_list('pk', flat=True))
        instituicoes_via_mantenedora_ids = set(Instituicao.objects.filter(mantenedora__in=perfil.mantenedoras.all()).values_list('pk', flat=True))

        # Junta todos os IDs únicos e busca os objetos de uma só vez
        todos_ids = instituicoes_diretas_ids.union(instituicoes_via_mantenedora_ids)
        context['instituicoes_acessiveis_usuario'] = Instituicao.objects.filter(pk__in=todos_ids).order_by('nome')

        # --- O RESTO DA LÓGICA CONTINUA ---
        instituicao_ativa_id = request.session.get('instituicao_ativa_id')
        if instituicao_ativa_id:
            try:
                # Filtra dentro das instituições acessíveis para segurança
                context['instituicao_ativa'] = context['instituicoes_acessiveis_usuario'].get(pk=instituicao_ativa_id)
            except Instituicao.DoesNotExist:
                context['instituicao_ativa'] = None
                if 'instituicao_ativa_id' in request.session:
                    del request.session['instituicao_ativa_id']

        # Lógica das Notificações
        notificacoes = Notificacao.objects.filter(destinatario=request.user)
        context['notificacoes_nao_lidas_count'] = notificacoes.filter(lida=False).count()
        context['notificacoes_recentes'] = notificacoes.order_by('-data_criacao')[:5]

    except Perfil.DoesNotExist:
        pass

    return context