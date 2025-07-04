# Arquivo: core/notificacoes.py

from .models import Notificacao

def criar_notificacao(usuario, mensagem, link=None):
    """
    Cria uma nova notificação na base de dados para um usuário específico.
    """
    if not usuario:
        return

    Notificacao.objects.create(
        usuario=usuario, # <--- CORREÇÃO: Mude 'destinatario' para 'usuario'
        mensagem=mensagem,
        link=link
    )