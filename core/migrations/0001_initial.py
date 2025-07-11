# Generated by Django 5.2.3 on 2025-07-04 22:47

import core.models
import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Eixo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField()),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Eixo de Avaliação',
                'verbose_name_plural': 'Eixos de Avaliação',
                'ordering': ['numero'],
            },
        ),
        migrations.CreateModel(
            name='Mantenedora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('cnpj', models.CharField(max_length=18, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Mantenedoras',
            },
        ),
        migrations.CreateModel(
            name='TipoProcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('descricao', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Tipo de Processo',
                'verbose_name_plural': 'Tipos de Processos',
            },
        ),
        migrations.CreateModel(
            name='Indicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10)),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('eixo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicadores', to='core.eixo')),
            ],
            options={
                'verbose_name': 'Indicador de Avaliação',
                'verbose_name_plural': 'Indicadores de Avaliação',
                'ordering': ['eixo__numero', 'numero'],
                'unique_together': {('eixo', 'numero')},
            },
        ),
        migrations.CreateModel(
            name='InstrumentoAvaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text="Nome completo do instrumento de avaliação, ex: 'IAIE Credenciamento'", max_length=255, unique=True)),
                ('tipo', models.CharField(choices=[('IAIE', 'Avaliação Institucional Externa (IAIE)'), ('IACG', 'Avaliação de Cursos de Graduação (IACG)')], help_text='Tipo principal do instrumento (Institucional ou Curso)', max_length=4)),
                ('subtipo', models.CharField(choices=[('CRI', 'Credenciamento (Institucional)'), ('RCI', 'Recredenciamento (Institucional)'), ('AC', 'Autorização (Curso)'), ('RC', 'Reconhecimento e Renovação de Reconhecimento (Curso)')], help_text='Subtipo específico do instrumento (Credenciamento, Autorização, etc.)', max_length=3)),
                ('versao', models.CharField(blank=True, help_text="Versão do instrumento, ex: '2023.2'", max_length=50, null=True)),
                ('ativo', models.BooleanField(default=True, help_text='Indica se o instrumento está ativo e pode ser usado em novos processos')),
            ],
            options={
                'verbose_name': 'Instrumento de Avaliação',
                'verbose_name_plural': 'Instrumentos de Avaliação',
                'unique_together': {('tipo', 'subtipo', 'versao')},
            },
        ),
        migrations.AddField(
            model_name='eixo',
            name='instrumento_avaliacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eixos', to='core.instrumentoavaliacao'),
        ),
        migrations.CreateModel(
            name='LogAtividade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora', models.DateTimeField(auto_now_add=True)),
                ('acao', models.CharField(max_length=255)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Log de Atividade',
                'verbose_name_plural': 'Logs de Atividades',
                'ordering': ['-data_hora'],
            },
        ),
        migrations.CreateModel(
            name='Instituicao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('sigla', models.CharField(blank=True, max_length=20, null=True)),
                ('cnpj', models.CharField(max_length=18, unique=True)),
                ('imagem_fundo', models.ImageField(blank=True, null=True, upload_to=core.models.get_background_filename)),
                ('mantenedora', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instituicoes', to='core.mantenedora')),
            ],
            options={
                'verbose_name_plural': 'Instituições',
            },
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensagem', models.TextField()),
                ('link', models.URLField(blank=True, max_length=500, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('lida', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificação',
                'verbose_name_plural': 'Notificações',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='Pasta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subpastas', to='core.pasta')),
            ],
            options={
                'verbose_name_plural': 'Pastas',
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_documento', models.CharField(max_length=255)),
                ('arquivo', models.FileField(upload_to=core.models.get_document_filename)),
                ('data_upload', models.DateTimeField(auto_now_add=True)),
                ('versao', models.CharField(blank=True, max_length=20, null=True)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('pasta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='core.pasta')),
            ],
            options={
                'verbose_name_plural': 'Documentos',
                'ordering': ['nome_documento'],
            },
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cargo', models.CharField(blank=True, max_length=100, null=True)),
                ('foto', models.ImageField(blank=True, null=True, upload_to=core.models.get_image_filename)),
                ('instituicoes', models.ManyToManyField(blank=True, related_name='responsaveis', to='core.instituicao')),
                ('mantenedoras', models.ManyToManyField(blank=True, related_name='responsaveis', to='core.mantenedora')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlanoDeAcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_inicio', models.DateField(default=datetime.date.today)),
                ('data_conclusao_prevista', models.DateField(blank=True, null=True)),
                ('data_conclusao_real', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDENTE', 'Pendente'), ('EM_ANDAMENTO', 'Em Andamento'), ('CONCLUIDO', 'Concluido'), ('ATRASADO', 'Atrasado'), ('CANCELADO', 'Cancelado')], default='PENDENTE', max_length=50)),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='planos_de_acao_responsavel', to='core.perfil')),
            ],
            options={
                'verbose_name': 'Plano de Ação',
                'verbose_name_plural': 'Planos de Ação',
                'ordering': ['-data_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Prazo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=255)),
                ('data_limite', models.DateField()),
                ('concluido', models.BooleanField(default=False)),
                ('plano_acao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prazos', to='core.planodeacao')),
            ],
            options={
                'verbose_name': 'Prazo',
                'verbose_name_plural': 'Prazos',
                'ordering': ['data_limite'],
            },
        ),
        migrations.CreateModel(
            name='ProcessoRegulatorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_protocolo', models.DateField(default=datetime.date.today)),
                ('data_conclusao_prevista', models.DateField(blank=True, null=True)),
                ('data_conclusao_real', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('EM_ANDAMENTO', 'Em Andamento'), ('AGUARDANDO_INFORMACAO', 'Aguardando Informação'), ('AGUARDANDO_AVALIACAO', 'Aguardando Avaliação'), ('SUSPENSO', 'Suspenso'), ('CONCLUIDO', 'Concluído'), ('CANCELADO', 'Cancelado')], default='EM_ANDAMENTO', max_length=50)),
                ('instituicao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processos', to='core.instituicao')),
                ('instrumento_avaliacao', models.ForeignKey(blank=True, help_text='Instrumento de avaliação do MEC aplicável a este processo.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='processos', to='core.instrumentoavaliacao')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processos_responsavel', to='core.perfil')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='processos', to='core.tipoprocesso')),
            ],
            options={
                'verbose_name': 'Processo Regulatório',
                'verbose_name_plural': 'Processos Regulatórios',
                'ordering': ['-data_protocolo'],
            },
        ),
        migrations.AddField(
            model_name='planodeacao',
            name='processo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planos_de_acao', to='core.processoregulatorio'),
        ),
        migrations.AddField(
            model_name='pasta',
            name='processo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pastas', to='core.processoregulatorio'),
        ),
        migrations.CreateModel(
            name='Simulacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_simulacao', models.DateField(default=datetime.date.today)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('processo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='simulacoes', to='core.processoregulatorio')),
                ('realizada_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.perfil')),
            ],
            options={
                'verbose_name': 'Simulação de Avaliação',
                'verbose_name_plural': 'Simulações de Avaliação',
                'ordering': ['-data_simulacao'],
            },
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('codigo_emec', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('nivel', models.CharField(choices=[('GRADUACAO', 'Graduação'), ('POS_GRADUACAO', 'Pós-Graduação')], default='GRADUACAO', max_length=20)),
                ('instituicao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cursos', to='core.instituicao')),
            ],
            options={
                'verbose_name_plural': 'Cursos',
                'unique_together': {('instituicao', 'nome')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='eixo',
            unique_together={('instrumento_avaliacao', 'numero')},
        ),
        migrations.AlterUniqueTogether(
            name='pasta',
            unique_together={('processo', 'parent', 'nome')},
        ),
        migrations.CreateModel(
            name='NotaSimulada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.DecimalField(decimal_places=1, max_digits=3)),
                ('justificativa', models.TextField(blank=True, null=True)),
                ('indicador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notas_simuladas', to='core.indicador')),
                ('simulacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notas', to='core.simulacao')),
            ],
            options={
                'verbose_name': 'Nota Simulada',
                'verbose_name_plural': 'Notas Simuladas',
                'unique_together': {('simulacao', 'indicador')},
            },
        ),
    ]
