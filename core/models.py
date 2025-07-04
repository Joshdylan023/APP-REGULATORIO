# Arquivo: core/models.py

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Mantenedora(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name="Razão Social")
    cnpj = models.CharField(max_length=18, unique=True, help_text="Formato: XX.XXX.XXX/XXXX-XX")
    def __str__(self):
        return self.razao_social

class Instituicao(models.Model):
    mantenedora = models.ForeignKey(Mantenedora, on_delete=models.PROTECT, verbose_name="Mantenedora")
    nome = models.CharField(max_length=255, verbose_name="Nome da Instituição")
    sigla = models.CharField(max_length=20)
    codigo_mec = models.IntegerField(unique=True, verbose_name="Código e-MEC")
    imagem_fundo = models.ImageField(upload_to='backgrounds/', null=True, blank=True, verbose_name="Imagem de Fundo (Opcional)")
    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"
    def __str__(self):
        return self.nome

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    mantenedoras = models.ManyToManyField(Mantenedora, blank=True, verbose_name="Mantenedoras Acessíveis")
    instituicoes = models.ManyToManyField(Instituicao, blank=True, verbose_name="Instituições Acessíveis (Controle Granular)")
    cargo = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True, default='fotos_perfil/default.png')
    def __str__(self):
        return self.user.username

class Curso(models.Model):
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, verbose_name="Instituição")
    nome = models.CharField(max_length=200)
    codigo_mec = models.IntegerField(unique=True, null=True, blank=True, verbose_name="Código do Curso (e-MEC)")
    def __str__(self):
        return f"{self.nome} ({self.instituicao.sigla})"

class ProcessoRegulatorio(models.Model):
    TIPO_PROCESSO_CHOICES = [('CRIACAO_IES', 'Criação da IES'), ('CREDENCIAMENTO', 'Credenciamento'), ('RECREDENCIAMENTO', 'Recredenciamento'), ('TRANSF_CENTRO', 'Transformação em Centro Universitário/Universidade'), ('AUTORIZACAO_CURSO', 'Autorização de Curso'), ('RECONHECIMENTO_CURSO', 'Reconhecimento de Curso'), ('RENOVACAO_RECONHECIMENTO', 'Renovação de Reconhecimento'), ('EXTINCAO_CURSO', 'Extinção Voluntária de Curso')]
    STATUS_CHOICES = [('NAO_INICIADO', 'Não Iniciado'), ('EM_ANDAMENTO', 'Em Andamento'), ('AGUARDANDO_MEC', 'Aguardando MEC'), ('CONCLUIDO', 'Concluído'), ('ARQUIVADO', 'Arquivado')]
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE, verbose_name="Instituição")
    tipo_processo = models.CharField(max_length=30, choices=TIPO_PROCESSO_CHOICES, verbose_name="Tipo de Processo")
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Curso")
    protocolo_mec = models.CharField(max_length=100, blank=True, verbose_name="Protocolo e-MEC")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NAO_INICIADO')
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Responsável")
    class Meta:
        verbose_name = "Processo Regulatório"
        verbose_name_plural = "Processos Regulatórios"
    def __str__(self):
        if self.curso: return f"{self.get_tipo_processo_display()} - {self.curso.nome}"
        return f"{self.get_tipo_processo_display()} - {self.instituicao.sigla}"

class Pasta(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Pasta")
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='pastas')
    pasta_pai = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subpastas', verbose_name="Pasta Pai")
    data_criacao = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nome

class Documento(models.Model):
    pasta = models.ForeignKey(Pasta, on_delete=models.CASCADE, related_name='documentos')
    titulo = models.CharField(max_length=200, verbose_name="Título do Documento")
    arquivo = models.FileField(upload_to='documentos/')
    data_upload = models.DateTimeField(auto_now_add=True)
    usuario_upload = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Enviado por")
    def __str__(self):
        return self.titulo

class Eixo(models.Model):
    INSTRUMENTO_CHOICES = [('CURSO', 'Instrumento de Avaliação de Cursos de Graduação (ACG)'), ('IES', 'Instrumento de Avaliação Institucional Externo (AIE)')]
    nome = models.CharField(max_length=255)
    instrumento = models.CharField(max_length=5, choices=INSTRUMENTO_CHOICES, default='IES', verbose_name="Tipo de Instrumento de Avaliação")
    def __str__(self):
        return f"({self.get_instrumento_display()}) - {self.nome}"

class Indicador(models.Model):
    eixo = models.ForeignKey(Eixo, on_delete=models.CASCADE, related_name='indicadores')
    codigo = models.CharField(max_length=10, verbose_name="Código")
    descricao = models.TextField(verbose_name="Descrição")
    def __str__(self):
        return f"{self.codigo} - {self.eixo.nome}"

class Simulacao(models.Model):
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE)
    nome_simulacao = models.CharField(max_length=200, verbose_name="Nome da Simulação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    def __str__(self):
        return self.nome_simulacao

class NotaSimulada(models.Model):
    simulacao = models.ForeignKey(Simulacao, related_name='notas', on_delete=models.CASCADE)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)
    nota = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    justificativa = models.TextField(blank=True, help_text="Evidências e justificativas para a nota atribuída")
    
class Notificacao(models.Model):
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    class Meta:
        ordering = ['-data_criacao']
    def __str__(self):
        return f"Notificação para {self.destinatario.username}: {self.mensagem[:30]}..."

class PlanoDeAcao(models.Model):
    STATUS_CHOICES = [('NAO_INICIADO', 'Não Iniciado'), ('EM_ANDAMENTO', 'Em Andamento'), ('CONCLUIDO', 'Concluído')]
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='planos_de_acao')
    descricao = models.TextField(verbose_name="Descrição da Ação")
    responsavel_acao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acoes_responsaveis', verbose_name="Responsável pela Ação")
    data_limite = models.DateField(null=True, blank=True, verbose_name="Data Limite")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NAO_INICIADO', verbose_name="Status")
    def __str__(self):
        return f"Ação para {self.processo.get_tipo_processo_display()}: {self.descricao[:50]}..."

class Prazo(models.Model):
    processo = models.ForeignKey(ProcessoRegulatorio, on_delete=models.CASCADE, related_name='prazos')
    descricao = models.CharField(max_length=255, verbose_name="Descrição do Prazo")
    data = models.DateField(verbose_name="Data")
    class Meta:
        ordering = ['data']
    def __str__(self):
        return f"{self.descricao} - {self.data.strftime('%d/%m/%Y')}"

class LogAtividade(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=255, verbose_name="Ação Realizada")
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    class Meta:
        ordering = ['-data_hora']
    def __str__(self):
        return f"{self.usuario} - {self.acao} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"