# Arquivo: core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProcessoRegulatorio, Documento, PlanoDeAcao, LogAtividade
from django.contrib.contenttypes.models import ContentType

def registrar_log(usuario, objeto, acao_desc):
    """Função auxiliar para criar a entrada de log."""
    LogAtividade.objects.create(
        usuario=usuario,
        acao=acao_desc,
        content_type=ContentType.objects.get_for_model(objeto),
        object_id=objeto.pk
    )

@receiver(post_save, sender=ProcessoRegulatorio)
def log_processo_salvo(sender, instance, created, **kwargs):
    """Disparado quando um ProcessoRegulatorio é salvo."""
    usuario = getattr(instance, '_last_user', instance.responsavel)
    if created:
        acao = f"Criou o processo '{instance}'"
    else:
        acao = f"Editou o processo '{instance}'"
    registrar_log(usuario, instance, acao)

@receiver(post_delete, sender=Documento)
def log_documento_deletado(sender, instance, **kwargs):
    """Disparado quando um Documento é deletado."""
    if instance.pasta and instance.pasta.processo:
        processo_pai = instance.pasta.processo
        usuario = processo_pai.responsavel
        acao = f"Excluiu o documento '{instance.titulo}' do processo '{processo_pai}'"
        registrar_log(usuario, processo_pai, acao)