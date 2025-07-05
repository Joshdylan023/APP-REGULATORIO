# Ficheiro: core/views.py (Versão final com acesso multi-institucional)

import io
import zipfile
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (DocumentoForm, PastaForm, PerfilFotoForm, PlanoDeAcaoForm,
                    PrazoForm, ProcessoForm)
from .models import (Documento, Eixo, Indicador, Instituicao, LogAtividade,
                     Mantenedora, NotaSimulada, Notificacao, Pasta, Perfil,
                     PlanoDeAcao, Prazo, ProcessoRegulatorio, Simulacao, TipoProcesso) # Adicione TipoProcesso se ainda não estiver aqui

from .notificacoes import criar_notificacao

User = get_user_model()

# --- DECORADOR AUXILIAR ---
def instituicao_selecionada_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('instituicao_ativa_id'):
            messages.warning(request, "Por favor, selecione uma instituição para continuar.")
            return redirect('selecionar_instituicao')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- VIEWS DE AUTENTICAÇÃO E SELEÇÃO ---

@login_required
def selecionar_instituicao_view(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    
    instituicoes_diretas = perfil.instituicoes.all()
    instituicoes_via_mantenedora = Instituicao.objects.filter(mantenedora__in=perfil.mantenedoras.all())
    instituicoes_acessiveis = (instituicoes_diretas | instituicoes_via_mantenedora).distinct()

    if request.method == 'POST':
        instituicao_id = request.POST.get('instituicao_id')
        if instituicao_id and instituicoes_acessiveis.filter(pk=instituicao_id).exists():
            instituicao_obj = get_object_or_404(Instituicao, pk=instituicao_id)
            request.session['instituicao_ativa_id'] = instituicao_obj.pk
            request.session['instituicao_ativa_nome'] = instituicao_obj.nome
            messages.success(request, f"Você está na instituição: {instituicao_obj.nome}")
            return redirect('dashboard')
            
    if instituicoes_acessiveis.count() == 1:
        instituicao = instituicoes_acessiveis.first()
        request.session['instituicao_ativa_id'] = instituicao.pk
        request.session['instituicao_ativa_nome'] = instituicao.nome
        return redirect('dashboard')

    return render(request, 'selecionar_instituicao.html', {'instituicoes_list': instituicoes_acessiveis})


@login_required
def perfil_view(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PerfilFotoForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'A sua foto de perfil foi atualizada!')
            return redirect('perfil')
    else:
        form = PerfilFotoForm(instance=perfil)
    context = {'form_foto': form}
    return render(request, 'perfil.html', context)


# --- VIEWS PRINCIPAIS (PROTEGIDAS) ---

@login_required
@instituicao_selecionada_required
def dashboard_view(request):
    instituicao_id = request.session.get('instituicao_ativa_id')
    instituicao_selecionada = get_object_or_404(Instituicao, pk=instituicao_id)
    
    filtro_tipo = request.GET.get('tipo', '')
    filtro_status = request.GET.get('status', '')
    lista_processos = ProcessoRegulatorio.objects.filter(instituicao=instituicao_selecionada)
    if filtro_tipo:
        lista_processos = lista_processos.filter(tipo__pk=filtro_tipo)
    if filtro_status:
        lista_processos = lista_processos.filter(status=filtro_status)
    todos_processos_list = lista_processos.order_by('-id')
    paginator = Paginator(todos_processos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj, 'instituicao_usuario': instituicao_selecionada,
        'tipos_processo': TipoProcesso.objects.all(), # Agora busca os objetos TipoProcesso
        'status_list': ProcessoRegulatorio.status_choices, # Acessa a tupla diretamente
        'filtro_tipo_atual': filtro_tipo, 'filtro_status_atual': filtro_status,
    }
    return render(request, 'dashboard.html', context)

@login_required
@instituicao_selecionada_required
def processo_detail_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    processo = get_object_or_404(ProcessoRegulatorio, pk=pk, instituicao_id=instituicao_id)
    
    historico_simulacoes = Simulacao.objects.filter(processo=processo).order_by('-data_simulacao')
    planos_de_acao = processo.planos_de_acao.all()
    # CORREÇÃO: Prazos agora estão ligados diretamente ao processo
    prazos = processo.prazos_processo.all().order_by('data_limite') # <-- CORREÇÃO AQUI (nome do related_name)

    conceito_final_ultima_simulacao = None
    ultima_simulacao = historico_simulacoes.first()
    if ultima_simulacao:
        notas_da_simulacao = [nota.nota for nota in ultima_simulacao.notas.all()]
        if notas_da_simulacao:
            media = sum(notas_da_simulacao) / len(notas_da_simulacao)
            conceito_final_ultima_simulacao = round(media, 2)
    
    if request.method == 'POST':
        form_plano_acao = PlanoDeAcaoForm(request.POST)
        form_prazo = PrazoForm(request.POST) 
        
        if 'submit_plano' in request.POST and form_plano_acao.is_valid():
            plano = form_plano_acao.save(commit=False)
            plano.processo = processo
            plano.save()
            messages.success(request, 'Novo item do Plano de Ação adicionado com sucesso!')
            return redirect('processo_detail', pk=pk)
        
        elif 'submit_prazo' in request.POST and form_prazo.is_valid():
            prazo = form_prazo.save(commit=False)
            prazo.processo = processo # <-- CORREÇÃO AQUI: Vincula o prazo diretamente ao processo
            prazo.save()
            messages.success(request, "Novo prazo adicionado com sucesso ao Processo!") # <-- MENSAGEM ALTERADA
            return redirect('processo_detail', pk=pk) # Redireciona de volta para a mesma página
    else:
        form_plano_acao = PlanoDeAcaoForm()
        form_prazo = PrazoForm()

    context = {
        'processo': processo, 'historico_simulacoes': historico_simulacoes,
        'planos_de_acao': planos_de_acao, 'prazos': prazos, # <-- Prazos atualizados
        'conceito_final_ultima_simulacao': conceito_final_ultima_simulacao,
        'form_plano_acao': form_plano_acao, 'form_prazo': form_prazo,
    }
    return render(request, 'processo_detail.html', context)

@login_required
@instituicao_selecionada_required
def processo_create_view(request):
    instituicao_id = request.session.get('instituicao_ativa_id')
    instituicao_ativa = get_object_or_404(Instituicao, pk=instituicao_id)

    if request.method == 'POST':
        form = ProcessoForm(request.POST)
        if form.is_valid():
            processo = form.save(commit=False)
            processo.instituicao = instituicao_ativa
            processo.responsavel = request.user.perfil # Responsavel é Perfil, não User
            processo.save()
            setattr(processo, '_last_user', request.user)
            messages.success(request, f"O processo '{processo.nome}' foi criado com sucesso!")
            criar_notificacao(request.user, f"Você criou o processo '{processo.nome}'.")
            return redirect('processo_detail', pk=processo.pk)
    else:
        form = ProcessoForm()
    context = {'form': form}
    return render(request, 'processo_form.html', context)


@login_required
@instituicao_selecionada_required
def processo_update_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    processo = get_object_or_404(ProcessoRegulatorio, pk=pk, instituicao_id=instituicao_id)
    if request.method == 'POST':
        form = ProcessoForm(request.POST, instance=processo)
        if form.is_valid():
            processo = form.save(commit=False)
            setattr(processo, '_last_user', request.user)
            processo.save()
            messages.success(request, "As alterações no processo foram salvas com sucesso!")
            return redirect('processo_detail', pk=processo.pk)
    else:
        form = ProcessoForm(instance=processo)
    context = {'form': form, 'processo': processo}
    return render(request, 'processo_form.html', context)


# --- VIEWS DO GED 2.0 ---

@login_required
@instituicao_selecionada_required
def ged_explorer_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    processo = get_object_or_404(ProcessoRegulatorio, pk=pk, instituicao_id=instituicao_id)
    pasta_atual_id = request.GET.get('pasta_id')
    pasta_atual = None
    if pasta_atual_id:
        pasta_atual = get_object_or_404(Pasta, pk=pasta_atual_id, processo=processo)
        subpastas = pasta_atual.subpastas.order_by('nome')
        documentos = pasta_atual.documentos.order_by('nome_documento')
    else:
        subpastas = processo.pastas.filter(parent__isnull=True).order_by('nome')
        documentos = []
    if request.method == 'POST':
        form_pasta = PastaForm(request.POST)
        form_documento = DocumentoForm(request.POST, request.FILES)
        if 'submit_pasta' in request.POST and form_pasta.is_valid():
            nova_pasta = form_pasta.save(commit=False)
            nova_pasta.processo = processo
            nova_pasta.parent = pasta_atual
            nova_pasta.save()
            messages.success(request, f"Pasta '{nova_pasta.nome}' criada com sucesso!")
            return redirect(request.get_full_path())
        elif 'submit_documento' in request.POST and form_documento.is_valid():
            if pasta_atual:
                documento = form_documento.save(commit=False)
                documento.pasta = pasta_atual
                documento.uploaded_by = request.user
                documento.save()
                messages.success(request, f"Documento '{documento.nome_documento}' enviado com sucesso!")
                return redirect(request.get_full_path())
            else:
                messages.error(request, "Selecione uma pasta para enviar o documento.")
    else:
        form_pasta = PastaForm()
        form_documento = DocumentoForm()
    context = {
        'processo': processo, 'pasta_atual': pasta_atual,
        'subpastas': subpastas, 'documentos': documentos,
        'form_pasta': form_pasta, 'form_documento': form_documento,
    }
    return render(request, 'ged_explorer.html', context)

@login_required
@instituicao_selecionada_required
def documento_delete_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    documento = get_object_or_404(Documento, pk=pk, pasta__processo__instituicao_id=instituicao_id)
    if request.method == 'POST':
        processo_pk = documento.pasta.processo.pk
        pasta_id = documento.pasta.id
        messages.warning(request, f"O documento '{documento.nome_documento}' foi excluído permanentemente.")
        documento.delete()
        return redirect(f"{reverse('ged_explorer', args=[processo_pk])}?pasta_id={pasta_id}")
    return redirect('dashboard')

@login_required
@instituicao_selecionada_required
def download_all_documents_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    processo = get_object_or_404(ProcessoRegulatorio, pk=pk, instituicao_id=instituicao_id)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pasta in processo.pastas.all():
            caminho_pasta = []
            p = pasta
            while p:
                caminho_pasta.insert(0, p.nome)
                p = p.parent
            caminho_no_zip = "/".join(caminho_pasta)
            for documento in pasta.documentos.all():
                if documento.arquivo:
                    with documento.arquivo.open('rb') as f:
                        conteudo_arquivo = f.read()
                        zip_file.writestr(f"{caminho_no_zip}/{documento.arquivo.name.split('/')[-1]}", conteudo_arquivo)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="documentos_processo_{pk}.zip"'
    return response

# --- VIEWS DE PLANOS DE AÇÃO ---

@login_required
@instituicao_selecionada_required
def plano_acao_update_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    plano_acao = get_object_or_404(PlanoDeAcao, pk=pk, processo__instituicao_id=instituicao_id)
    if request.method == 'POST':
        form = PlanoDeAcaoForm(request.POST, instance=plano_acao)
        if form.is_valid():
            form.save()
            messages.success(request, 'O item do Plano de Ação foi atualizado com sucesso!')
            return redirect('processo_detail', pk=plano_acao.processo.pk)
    else:
        form = PlanoDeAcaoForm(instance=plano_acao)
    context = {'form': form, 'plano_acao': plano_acao}
    return render(request, 'plano_acao_form.html', context)


# --- VIEWS DO SIMULADOR ---
@login_required
@instituicao_selecionada_required
def simulador_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    processo = get_object_or_404(ProcessoRegulatorio, pk=pk, instituicao_id=instituicao_id)
    
    # Lógica de filtro de instrumento (AGORA USA processo.instrumento_avaliacao)
    eixos = Eixo.objects.none() # Inicializa como QuerySet vazio
    if processo.instrumento_avaliacao: # Verifica se um instrumento está associado
        eixos = Eixo.objects.filter(instrumento_avaliacao=processo.instrumento_avaliacao).prefetch_related('indicadores').all()
    
    # Lógica para salvar a simulação
    if request.method == 'POST':
        # Validar se Eixos foram encontrados para este instrumento
        if not eixos.exists():
            messages.error(request, "Não há eixos configurados para o instrumento de avaliação deste processo.")
            return redirect('simulador', pk=processo.pk)

        nova_simulacao = Simulacao.objects.create(
            processo=processo, 
            # Use o nome do processo e do instrumento para o nome da simulação
            nome_simulacao=f"Simulação de {processo.nome} - {processo.instrumento_avaliacao.nome if processo.instrumento_avaliacao else 'Sem Instrumento'} em {timezone.now().strftime('%d/%m/%Y')}",
            realizada_por=request.user.perfil
        )
        for key, value in request.POST.items():
            if key.startswith('nota-'):
                indicador_id = int(key.split('-')[1])
                # Verifique se o indicador pertence aos eixos do instrumento selecionado
                if Indicador.objects.filter(pk=indicador_id, eixo__instrumento_avaliacao=processo.instrumento_avaliacao).exists():
                    NotaSimulada.objects.create(
                        simulacao=nova_simulacao, 
                        indicador_id=indicador_id, 
                        nota=float(value)
                    )
        messages.success(request, "Simulação salva com sucesso!")
        return redirect('simulacao_resultado', pk=nova_simulacao.pk)
    
    context = {
        'processo': processo,
        'eixos': eixos
    }
    
    return render(request, 'simulador.html', context)


# Em core/views.py

@login_required
@instituicao_selecionada_required
def simulacao_update_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    simulacao = get_object_or_404(Simulacao, pk=pk, processo__instituicao_id=instituicao_id)
    processo = simulacao.processo

    # Lógica de filtro de instrumento (AGORA USA processo.instrumento_avaliacao)
    eixos = Eixo.objects.none() # Inicializa como QuerySet vazio
    if processo.instrumento_avaliacao: # Verifica se um instrumento está associado
        eixos = Eixo.objects.filter(instrumento_avaliacao=processo.instrumento_avaliacao).prefetch_related('indicadores').all()

    # Carrega as notas já existentes para preencher o formulário
    notas_existentes = {nota.indicador_id: nota.nota for nota in simulacao.notas.all()}
    for eixo in eixos:
        for indicador in eixo.indicadores.all():
            indicador.nota_preenchida = notas_existentes.get(indicador.pk)

    # Lógica para salvar a simulação atualizada
    if request.method == 'POST':
        # Validar se Eixos foram encontrados para este instrumento
        if not eixos.exists():
            messages.error(request, "Não há eixos configurados para o instrumento de avaliação deste processo.")
            return redirect('simulador', pk=processo.pk)

        simulacao.notas.all().delete() # Apaga as notas antigas
        for key, value in request.POST.items():
            if key.startswith('nota-'):
                indicador_id = int(key.split('-')[1])
                # Verifique se o indicador pertence aos eixos do instrumento selecionado
                if Indicador.objects.filter(pk=indicador_id, eixo__instrumento_avaliacao=processo.instrumento_avaliacao).exists():
                    NotaSimulada.objects.create(
                        simulacao=simulacao,
                        indicador_id=indicador_id,
                        nota=float(value)
                    )
        messages.success(request, "Simulação atualizada com sucesso!")
        return redirect('simulacao_resultado', pk=simulacao.pk)

    context = {
        'processo': processo,
        'eixos': eixos,
        'simulacao': simulacao,
        'notas_existentes': notas_existentes,
    }

    return render(request, 'simulador.html', context)


@login_required
@instituicao_selecionada_required
def simulacao_resultado_view(request, pk):
    instituicao_id = request.session.get('instituicao_ativa_id')
    simulacao = get_object_or_404(Simulacao.objects.prefetch_related('notas__indicador__eixo'), pk=pk, processo__instituicao_id=instituicao_id)
    
    resultados_eixos = {}
    notas_gerais = []

    # Agrupa as notas por eixo
    for nota_simulada in simulacao.notas.all():
        eixo_nome = nota_simulada.indicador.eixo.nome
        if eixo_nome not in resultados_eixos:
            resultados_eixos[eixo_nome] = []
        resultados_eixos[eixo_nome].append(nota_simulada.nota)
        notas_gerais.append(nota_simulada.nota)

    # Calcula a média de cada eixo
    for eixo, notas in resultados_eixos.items():
        media = sum(notas) / len(notas) if notas else 0
        resultados_eixos[eixo] = round(media, 2)

    # Calcula o conceito final
    conceito_final = sum(notas_gerais) / len(notas_gerais) if notas_gerais else 0
    conceito_final = round(conceito_final, 2)

    # A DEFINIÇÃO DO CONTEXTO QUE ESTAVA A FALTAR
    context = {
        'simulacao': simulacao,
        'resultados_eixos': resultados_eixos,
        'conceito_final': conceito_final,
    }
    
    return render(request, 'simulacao_resultado.html', context)


# --- VIEWS DE API ---

@login_required
def processos_status_api_view(request):
    instituicao_id = request.session.get('instituicao_ativa_id')
    if not instituicao_id:
        return JsonResponse({'labels': [], 'data': []})
    contagem_status = (ProcessoRegulatorio.objects.filter(instituicao_id=instituicao_id).values('status').annotate(quantidade=Count('status')).order_by('status'))
    status_display_map = dict(ProcessoRegulatorio.status_choices)
    labels = [status_display_map.get(item['status'], item['status']) for item in contagem_status]
    data = [item['quantidade'] for item in contagem_status]
    return JsonResponse({'labels': labels, 'data': data})

@login_required
def simulacao_eixos_api_view(request):
    instituicao_id = request.session.get('instituicao_ativa_id')
    if not instituicao_id:
        return JsonResponse({'labels': [], 'data': []})
    ultima_simulacao = Simulacao.objects.filter(processo__instituicao_id=instituicao_id).order_by('-data_simulacao').first()
    labels, data = [], []
    if ultima_simulacao:
        resultado = (NotaSimulada.objects.filter(simulacao=ultima_simulacao).values('indicador__eixo__nome').annotate(media=Avg('nota')).order_by('indicador__eixo__nome'))
        for item in resultado:
            labels.append(item['indicador__eixo__nome'])
            data.append(round(item['media'], 2))
    return JsonResponse({'labels': labels, 'data': data})


@login_required
def marcar_notificacoes_como_lidas_api_view(request):
    if request.method == 'POST':
        # Aceda às notificações através do related_name 'notificacoes' no modelo User
        request.user.notificacoes.filter(lida=False).update(lida=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'bad request'}, status=400)