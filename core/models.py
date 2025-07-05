# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings
import os
import uuid
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Funções auxiliares para uploads
def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('fotos_perfil', filename)

def get_document_filename(instance, filename):
    ext = filename.split('.')[-1]
    # Usar o nome do documento (slugify se necessário) e um UUID para unicidade
    doc_name = instance.nome_documento if instance.nome_documento else "documento"
    filename = f"{doc_name}_{uuid.uuid4().hex}.{ext}"
    # Armazenar em uma pasta por processo, se aplicável, ou direto em 'documentos'
    if hasattr(instance, 'pasta') and instance.pasta:
        if hasattr(instance.pasta, 'processo') and instance.pasta.processo:
            return os.path.join('documentos', f'processo_{instance.pasta.processo.id}', filename)
    return os.path.join('documentos', filename)

def get_background_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('backgrounds', filename)

class Mantenedora(models.Model):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    # outros campos

    class Meta:
        verbose_name_plural = "Mantenedoras"

    def __str__(self):
        return self.nome

class Instituicao(models.Model):
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True)
    mantenedora = models.ForeignKey(Mantenedora, on_delete=models.SET_NULL, null=True, blank=True, related_name='instituicoes')
    imagem_fundo = models.ImageField(upload_to=get_background_filename, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Instituições"

    def __str__(self):
        return self.nome

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to=get_image_filename, blank=True, null=True)
    mantenedoras = models.ManyToManyField(Mantenedora, blank=True, related_name='responsaveis')
    instituicoes = models.ManyToManyField(Instituicao, blank=True, related_name='responsaveis')

    def __str__(self):
        return self.user.username

class TipoProcesso(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tipo de Processo"
        verbose_name_plural = "Tipos de Processos"

    def __str__(self):
        return self.nome

# NOVO MODELO: InstrumentoAvaliacao
class InstrumentoAvaliacao(models.Model):
    # Tipos de instrumentos como os que você descreveu
    TIPO_INSTITUCIONAL = 'IAIE'
    TIPO_CURSO = 'IACG'
    TIPOS_INSTRUMENTO = [
        (TIPO_INSTITUCIONAL, 'Avaliação Institucional Externa (IAIE)'),
        (TIPO_CURSO, 'Avaliação de Cursos de Graduação (IACG)'),
    ]

    # Subtipos que refinam o instrumento (Credenciamento, Autorização, etc.)
    SUBTIPO_CREDENCIAMENTO_INSTITUCIONAL = 'CRI'
    SUBTIPO_RECREDENCIAMENTO_INSTITUCIONAL = 'RCI'
    SUBTIPO_AUTORIZACAO_CURSO = 'AC'
    SUBTIPO_RECONHECIMENTO_CURSO = 'RC' # Inclui Renovação de Reconhecimento
    SUBTIPOS_INSTRUMENTO = [
        (SUBTIPO_CREDENCIAMENTO_INSTITUCIONAL, 'Credenciamento (Institucional)'),
        (SUBTIPO_RECREDENCIAMENTO_INSTITUCIONAL, 'Recredenciamento (Institucional)'),
        (SUBTIPO_AUTORIZACAO_CURSO, 'Autorização (Curso)'),
        (SUBTIPO_RECONHECIMENTO_CURSO, 'Reconhecimento e Renovação de Reconhecimento (Curso)'),
    ]

    nome = models.CharField(max_length=255, unique=True, help_text="Nome completo do instrumento de avaliação, ex: 'IAIE Credenciamento'")
    tipo = models.CharField(max_length=4, choices=TIPOS_INSTRUMENTO, help_text="Tipo principal do instrumento (Institucional ou Curso)")
    subtipo = models.CharField(max_length=3, choices=SUBTIPOS_INSTRUMENTO, help_text="Subtipo específico do instrumento (Credenciamento, Autorização, etc.)")
    versao = models.CharField(max_length=50, blank=True, null=True, help_text="Versão do instrumento, ex: '2023.2'")
    ativo = models.BooleanField(default=True, help_text="Indica se o instrumento está ativo e pode ser usado em novos processos")

    class Meta:
        verbose_name = "Instrumento de Avaliação"
        verbose_name_plural = "Instrumentos de Avaliação"
        unique_together = ('tipo', 'subtipo', 'versao') # Garante que não há instrumentos duplicados na mesma versão

    def __str__(self):
        versao_str = f" (v.{self.versao})" if self.versao else ""
        return f"{self.get_tipo_display()} - {self.get_subtipo_display()}{versao_str}"

# --- INÍCIO DA CORREÇÃO: CLASSE CURSO MOVIDA PARA ANTES DE PROCESSOREGULATORIO ---
class Curso(models.Model): 
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, related_name='cursos')
    nome = models.CharField(max_length=200)
    codigo_eMEC = models.CharField(max_length=20, blank=True, null=True, unique=True)
    nivel_choices = [
        ('GRADUACAO', 'Graduação'),
        ('POS_GRADUACAO', 'Pós-Graduação'),
    ]
    nivel = models.CharField(max_length=20, choices=nivel_choices, default='GRADUACAO')

    class Meta:
        unique_together = ('instituicao', 'nome')
        verbose_name_plural = "Cursos"

    def __str__(self):
        return f"{self.nome} ({self.instituicao.sigla or self.instituicao.nome})"
# --- FIM DA CORREÇÃO: CLASSE CURSO MOVIDA ---

# MODIFICAR ProcessoRegulatorio para vincular a InstrumentoAvaliacao
class ProcessoRegulatorio(models.Model):
    # Tipos de processo já existentes
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, related_name='processos')
    tipo = models.ForeignKey(TipoProcesso, on_delete=models.PROTECT, related_name='processos')
    instrumento_avaliacao = models.ForeignKey(InstrumentoAvaliacao, on_delete=models.PROTECT, related_name='processos', null=True, blank=True,
                                              help_text="Instrumento de avaliação do MEC aplicável a este processo.")
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True, related_name='processos_relacionados', help_text="Curso relacionado a este processo, se aplicável.") 
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    data_protocolo = models.DateField(default=date.today)
    data_conclusao_prevista = models.DateField(blank=True, null=True)
    data_conclusao_real = models.DateField(blank=True, null=True)
    status_choices = [
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('AGUARDANDO_INFORMACAO', 'Aguardando Informação'),
        ('AGUARDANDO_AVALIACAO', 'Aguardando Avaliação'),
        ('SUSPENSO', 'Suspenso'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='EM_ANDAMENTO')
    responsavel = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, related_name='processos_responsavel')
    # Outros campos do ProcessoRegulatorio...

    class Meta:
        verbose_name = "Processo Regulatório"
        verbose_name_plural = "Processos Regulatórios"
        ordering = ['-data_protocolo']

    def __str__(self):
        return f"{self.nome} ({self.instituicao.sigla or self.instituicao.nome})"

    def clean(self):
        super().clean()
        # Validação para garantir que o instrumento de avaliação é compatível com o tipo de processo
        if self.instrumento_avaliacao and self.tipo:
            # Mapeamento simplificado dos tipos de processo para tipos de instrumento
            # Você pode expandir esta lógica conforme necessário
            compatibilidade_map = {
                'Credenciamento': InstrumentoAvaliacao.TIPO_INSTITUCIONAL,
                'Recredenciamento': InstrumentoAvaliacao.TIPO_INSTITUCIONAL,
                'Autorização': InstrumentoAvaliacao.TIPO_CURSO,
                'Reconhecimento': InstrumentoAvaliacao.TIPO_CURSO, # Assumindo que este TipoProcesso cobre Reconhecimento e Renovação
            }
            
            expected_instrument_type = compatibilidade_map.get(self.tipo.nome)
            
            if expected_instrument_type and self.instrumento_avaliacao.tipo != expected_instrument_type:
                raise ValidationError(
                    f"O Instrumento de Avaliação selecionado ({self.instrumento_avaliacao.get_tipo_display()}) "
                    f"não é compatível com o Tipo de Processo '{self.tipo.nome}'."
                )

# MODIFICAR Eixo para vincular a InstrumentoAvaliacao
class Eixo(models.Model):
    instrumento_avaliacao = models.ForeignKey(InstrumentoAvaliacao, on_delete=models.CASCADE, related_name='eixos', null=True, blank=True)
    numero = models.IntegerField()
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Eixo de Avaliação"
        verbose_name_plural = "Eixos de Avaliação"
        ordering = ['numero']
        unique_together = ('instrumento_avaliacao', 'numero') # Eixos são únicos por instrumento e número

    def __str__(self):
        return f"Eixo {self.numero}: {self.nome} ({self.instrumento_avaliacao.nome})"

# MODIFICAR Indicador para vincular a Eixo
class Indicador(models.Model):
    eixo = models.ForeignKey(Eixo, on_delete=models.CASCADE, related_name='indicadores')
    numero = models.CharField(max_length=10) # Pode ser 1.1, 1.2, etc.
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Indicador de Avaliação"
        verbose_name_plural = "Indicadores de Avaliação"
        ordering = ['eixo__numero', 'numero'] # Ordena por eixo e depois pelo número do indicador
        unique_together = ('eixo', 'numero') # Indicadores são únicos por eixo e número

    def __str__(self):
        return f"E{self.eixo.numero}I{self.numero}: {self.nome} ({self.eixo.instrumento_avaliacao.nome})"

class Simulacao(models.Model):
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='simulacoes')
    nome_simulacao = models.CharField(max_length=255, help_text="Nome ou título da simulação.") # <-- ADICIONE ESTA LINHA
    data_simulacao = models.DateField(default=date.today)
    observacoes = models.TextField(blank=True, null=True)
    realizada_por = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Simulação de Avaliação"
        verbose_name_plural = "Simulações de Avaliação"
        ordering = ['-data_simulacao']

    def __str__(self):
        # Altere para retornar o nome da simulação se existir, senão o nome do processo
        return f"Simulação: {self.nome_simulacao or self.processo.nome} em {self.data_simulacao}"

class NotaSimulada(models.Model):
    simulacao = models.ForeignKey(Simulacao, on_delete=models.CASCADE, related_name='notas')
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='notas_simuladas')
    nota = models.DecimalField(max_digits=3, decimal_places=1) # Ex: 4.5
    justificativa = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Nota Simulada"
        verbose_name_plural = "Notas Simuladas"
        unique_together = ('simulacao', 'indicador') # Um indicador só pode ter uma nota por simulação

    def __str__(self):
        return f"Nota {self.nota} para {self.indicador.nome} na simulação {self.simulacao.id}"

class LogAtividade(models.Model):
    data_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=255)

    # Campos para a GenericForeignKey (certifique-se de que são estes os nomes e tipos)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id') # A relação genérica em si

    class Meta:
        verbose_name = "Log de Atividade"
        verbose_name_plural = "Logs de Atividades"
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.usuario.username if self.usuario else 'Sistema'} - {self.acao} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    link = models.URLField(max_length=500, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Para {self.usuario.username}: {self.mensagem[:50]}..."

class PlanoDeAcao(models.Model):
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='planos_de_acao')
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, related_name='planos_de_acao_responsavel')
    data_inicio = models.DateField(default=date.today)
    data_conclusao_prevista = models.DateField(blank=True, null=True)
    data_conclusao_real = models.DateField(blank=True, null=True)
    
    data_limite = models.DateField(null=True, blank=True, help_text="Data limite para a conclusão do Plano de Ação.") # <-- ADICIONE ESTA LINHA
    
    status_choices = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluido'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='PENDENTE')

    class Meta:
        verbose_name = "Plano de Ação"
        verbose_name_plural = "Planos de Ação"
        ordering = ['-data_inicio']

    def __str__(self):
        return self.titulo

class Prazo(models.Model):
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='prazos_processo')
    descricao = models.CharField(max_length=255)
    data_limite = models.DateField()
    concluido = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Prazo"
        verbose_name_plural = "Prazos"
        ordering = ['data_limite']

    def __str__(self):
        return f"{self.descricao} (Até: {self.data_limite.strftime('%d/%m/%Y')})"

class Pasta(models.Model):
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='pastas', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subpastas')
    nome = models.CharField(max_length=255)

    class Meta:
        unique_together = ('processo', 'parent', 'nome') # Pasta única por processo/parent/nome
        verbose_name_plural = "Pastas"

    def __str__(self):
        return self.nome

class Documento(models.Model):
    pasta = models.ForeignKey(Pasta, on_delete=models.CASCADE, related_name='documentos')
    nome_documento = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to=get_document_filename)
    data_upload = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    versao = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Documentos"
        ordering = ['nome_documento']

    def __str__(self):
        return self.nome_documento

# Sinal para registrar atividade após salvar um ProcessoRegulatorio
@receiver(post_save, sender=ProcessoRegulatorio)
def log_processo_save(sender, instance, created, **kwargs):
    acao = "criado" if created else "atualizado"
    
    # Lógica mais robusta para determinar o usuário que realizou a ação
    acting_user = None
    if hasattr(instance, '_last_user') and instance._last_user is not None:
        # Preferir o usuário definido explicitamente na view (_last_user)
        acting_user = instance._last_user
    elif instance.responsavel:
        # Se não houver _last_user, usar o User associado ao Perfil responsável do processo
        acting_user = instance.responsavel.user
    
    LogAtividade.objects.create(
        usuario=acting_user, # Garante que seja um objeto User ou None
        acao=f"Processo Regulatório '{instance.nome}' {acao}.",
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id
    )

# Sinal para registrar atividade após deletar um ProcessoRegulatorio
@receiver(post_delete, sender=ProcessoRegulatorio)
def log_processo_delete(sender, instance, **kwargs):
    acao = "deletado"
    
    acting_user = None
    if hasattr(instance, '_last_user') and instance._last_user is not None:
        acting_user = instance._last_user
    elif instance.responsavel:
        acting_user = instance.responsavel.user
    
    # --- LINHAS DE DEPURACÃO ---
    print(f"DEBUG LOG: log_processo_delete - acting_user type: {type(acting_user)}, value: {acting_user}")
    # --- FIM LINHAS DE DEPURACÃO ---

    LogAtividade.objects.create(
        usuario=acting_user, # Garante que seja um objeto User ou None
        acao=f"Processo Regulatório '{instance.nome}' {acao}.",
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id
    )
    
# Sinal para registrar atividade após salvar um Documento
@receiver(post_save, sender=Documento)
def log_documento_save(sender, instance, created, **kwargs):
    acao = "carregado" if created else "atualizado"
    processo = instance.pasta.processo if instance.pasta and instance.pasta.processo else None
    acao_msg = f"Documento '{instance.nome_documento}' {acao}."
    if processo:
        acao_msg += f" (Processo: {processo.nome})"
    
    # --- LINHAS DE DEPURACÃO ---
    print(f"DEBUG LOG: log_documento_save - usuario type: {type(instance.uploaded_by)}, value: {instance.uploaded_by}")
    # --- FIM LINHAS DE DEPURACÃO ---

    LogAtividade.objects.create(
        usuario=instance.uploaded_by, # instance.uploaded_by é um User, deve estar correto
        acao=acao_msg,
        content_type=ContentType.objects.get_for_model(instance), # <--- CORREÇÃO AQUI
       object_id=instance.id # <--- CORREÇÃO AQUI
    )

# Sinal para registrar atividade após deletar um Documento
@receiver(post_delete, sender=Documento)
def log_documento_delete(sender, instance, **kwargs):
    processo = instance.pasta.processo if instance.pasta and instance.pasta.processo else None
    acao_msg = f"Documento '{instance.nome_documento}' deletado."
    if processo:
        acao_msg += f" (Processo: {processo.nome})"

    # --- LINHAS DE DEPURACÃO ---
    print(f"DEBUG LOG: log_documento_delete - usuario type: {type(instance.uploaded_by)}, value: {instance.uploaded_by}")
    # --- FIM LINHAS DE DEPURACÃO ---

    LogAtividade.objects.create(
        usuario=instance.uploaded_by, # O usuário que deletou pode ser diferente do uploaded_by
        acao=acao_msg,
        content_type=ContentType.objects.get_for_model(instance), # <--- CORREÇÃO AQUI
        object_id=instance.id # <--- CORREÇÃO AQUI
    )