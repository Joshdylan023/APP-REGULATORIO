# Arquivo: core/management/commands/enviar_alertas.py (Versão Final)

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.urls import reverse
from django.contrib.sites.models import Site
from datetime import timedelta
from core.models import ProcessoRegulatorio
# Importamos nossa função para criar notificações no sino
from core.notificacoes import criar_notificacao

class Command(BaseCommand):
    help = 'Verifica processos com prazo nos próximos 30 dias e envia alertas.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando verificação de prazos...'))
        
        hoje = timezone.now().date()
        data_limite = hoje + timedelta(days=30)

        processos_para_alertar = ProcessoRegulatorio.objects.exclude(
            status__in=['CONCLUIDO', 'ARQUIVADO']
        ).filter(
            data_protocolo_final__gte=hoje,
            data_protocolo_final__lte=data_limite
        )

        if not processos_para_alertar.exists():
            self.stdout.write('Nenhum processo com prazo nos próximos 30 dias.')
            return

        for processo in processos_para_alertar:
            responsavel = processo.responsavel
            if responsavel:
                dias_restantes = (processo.data_protocolo_final - hoje).days
                
                # --- Prepara a Mensagem e o Link ---
                assunto = f"[ALERTA DE PRAZO] Processo {processo.get_tipo_processo_display()}"
                mensagem_base = (
                    f"O processo '{processo.get_tipo_processo_display()}' "
                    f"referente ao curso '{processo.curso.nome if processo.curso else 'N/A'}' "
                    f"tem um prazo final em {dias_restantes} dias ({processo.data_protocolo_final.strftime('%d/%m/%Y')})."
                )
                
                # Monta o link completo para a página do processo
                # (Isto pode precisar de configuração em produção)
                domain = Site.objects.get_current().domain
                link_processo = f"http://{domain}{reverse('processo_detail', args=[processo.pk])}"

                # --- 1. CRIA A NOTIFICAÇÃO NO SINO ---
                criar_notificacao(
                    usuario=responsavel,
                    mensagem=mensagem_base,
                    link=link_processo
                )
                self.stdout.write(self.style.SUCCESS(f"Notificação no sino criada para '{responsavel.username}'."))

                # --- 2. ENVIA O E-MAIL (se o usuário tiver um cadastrado) ---
                if responsavel.email:
                    mensagem_email = f"""
                    Olá, {responsavel.get_full_name() or responsavel.username},

                    Este é um alerta automático do Sistema de Gestão Regulatória.
                    
                    {mensagem_base}

                    Para ver os detalhes, acesse: {link_processo}

                    Atenciosamente,
                    Sistema de Gestão Regulatória.
                    """
                    send_mail(
                        assunto,
                        mensagem_email,
                        'sistema@sua-ies.com',
                        [responsavel.email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f"Alerta de e-mail enviado para '{responsavel.email}'."))
                else:
                    self.stdout.write(self.style.WARNING(f"Responsável '{responsavel.username}' não possui e-mail para alerta."))

        self.stdout.write(self.style.SUCCESS('Verificação de prazos concluída.'))