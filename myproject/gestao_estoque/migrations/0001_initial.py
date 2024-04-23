# Generated by Django 4.2.11 on 2024-04-21 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("controle_medicamentos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Estoque",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantidade", models.IntegerField()),
                ("quantidade_minima", models.IntegerField()),
                (
                    "medicamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="controle_medicamentos.medicamento",
                    ),
                ),
            ],
        ),
    ]