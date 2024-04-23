# Generated by Django 4.2.11 on 2024-04-21 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Morador",
            fields=[
                (
                    "cpf",
                    models.CharField(max_length=11, primary_key=True, serialize=False),
                ),
                ("nome", models.CharField(max_length=50)),
                ("dt_nascimento", models.DateField()),
            ],
        ),
    ]