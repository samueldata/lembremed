# Generated by Django 5.0.3 on 2024-05-06 22:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Apresentacao',
            fields=[
                ('codigo', models.AutoField(primary_key=True, serialize=False)),
                ('unidade_prescricao', models.CharField(max_length=100)),
                ('unidade_comercial', models.CharField(max_length=100)),
                ('razao_prescricao_comercial', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instituicao',
            fields=[
                ('cnpj', models.IntegerField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=50)),
                ('senha', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Medicamento',
            fields=[
                ('codigo', models.AutoField(primary_key=True, serialize=False)),
                ('principio', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Morador',
            fields=[
                ('cpf', models.IntegerField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=50)),
                ('dt_nascimento', models.DateField()),
            ],
            options={
                'permissions': (('pode_gerenciar_morador', 'Pode gerenciar os moradores'), ('pode_medicar_morador', 'Pode administrar medicamentos nos moradores')),
            },
        ),
        migrations.CreateModel(
            name='Estoque',
            fields=[
                ('codigo', models.AutoField(primary_key=True, serialize=False)),
                ('concentracao', models.CharField(max_length=50)),
                ('prescricao', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('qtd_disponivel', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('frequencia', models.IntegerField(default=1)),
                ('horarios', models.CharField(max_length=150)),
                ('apresentacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lembremed.apresentacao')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lembremed.medicamento')),
                ('morador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lembremed.morador')),
            ],
        ),
        migrations.CreateModel(
            name='Profissional',
            fields=[
                ('cpf', models.IntegerField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=50)),
                ('coren', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('pode_gerenciar_profissional', 'Pode gerenciar os profissionais'),),
            },
        ),
        migrations.CreateModel(
            name='Administra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dthr_administracao', models.DateTimeField(null=True)),
                ('estoque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lembremed.estoque')),
                ('morador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lembremed.morador')),
                ('profissional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lembremed.profissional')),
            ],
        ),
    ]
