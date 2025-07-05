# Arquivo: core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProcessoRegulatorio, Documento, PlanoDeAcao, LogAtividade # Mantenha LogAtividade
from django.contrib.contenttypes.models import ContentType

def registrar_log(usuario, objeto, acao_desc):
    """Função auxiliar para criar a entrada de log."""
    # Garante que usuario seja um objeto User ou None
    # Esta linha foi simplificada para a depuração anterior.
    # Se acting_user for usado, ele deve ser passado como parametro 'usuario'.
    
    # Adicionei um print de depuração para garantir que o tipo e valor estejam corretos AQUI
    print(f"DEBUG LOG (signals.py): registrar_log - usuario type: {type(usuario)}, value: {usuario}")

    LogAtividade.objects.create(
        # CORREÇÃO PRINCIPAL: Passe o ID do usuário em vez do objeto completo
        usuario_id=usuario.pk if usuario else None, 
        acao=acao_desc,
        content_type=ContentType.objects.get_for_model(objeto),
        object_id=objeto.pk
    )

@receiver(post_save, sender=ProcessoRegulatorio)
def log_processo_salvo(sender, instance, created, **kwargs):
    acao = "criado" if created else "atualizado"
    
    acting_user = None
    if hasattr(instance, '_last_user') and instance._last_user is not None:
        acting_user = instance._last_user
    elif instance.responsavel:
        acting_user = instance.responsavel.user
    
    # O print de depuração AQUI é do models.py, mova para signals.py ou use o do registrar_log
    # print(f"DEBUG LOG: log_processo_save - acting_user type: {type(acting_user)}, value: {acting_user}")

    registrar_log(acting_user, instance, acao) # Passe acting_user para registrar_log

@receiver(post_delete, sender=ProcessoRegulatorio)
def log_processo_deletado(sender, instance, **kwargs):
    acao = "deletado"
    
    acting_user = None
    if hasattr(instance, '_last_user') and instance._last_user is not None:
        acting_user = instance._last_user
    elif instance.responsavel:
        acting_user = instance.responsavel.user
    
    # O print de depuração AQUI é do models.py, mova para signals.py ou use o do registrar_log
    # print(f"DEBUG LOG: log_processo_delete - acting_user type: {type(acting_user)}, value: {acting_user}")

    registrar_log(acting_user, instance, acao)

@receiver(post_save, sender=Documento)
def log_documento_salvo(sender, instance, created, **kwargs):
    acao = "carregado" if created else "atualizado"
    processo = instance.pasta.processo if instance.pasta and instance.pasta.processo else None
    acao_msg = f"Documento '{instance.nome_documento}' {acao}."
    if processo:
        acao_msg += f" (Processo: {processo.nome})"
    
    # O print de depuração AQUI é do models.py, mova para signals.py ou use o do registrar_log
    # print(f"DEBUG LOG: log_documento_save - usuario type: {type(instance.uploaded_by)}, value: {instance.uploaded_by}")

    registrar_log(instance.uploaded_by, instance, acao_msg)

@receiver(post_delete, sender=Documento)
def log_documento_deletado(sender, instance, **kwargs):
    processo = instance.pasta.processo if instance.pasta and instance.pasta.processo else None
    acao_msg = f"Documento '{instance.nome_documento}' deletado."
    if processo:
        acao_msg += f" (Processo: {processo.nome})"

    # O print de depuração AQUI é do models.py, mova para signals.py ou use o do registrar_log
    # print(f"DEBUG LOG: log_documento_delete - usuario type: {type(instance.uploaded_by)}, value: {instance.uploaded_by}")

    registrar_log(instance.uploaded_by, instance, acao_msg)