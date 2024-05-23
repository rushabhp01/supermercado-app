# Generated by Django 5.0.5 on 2024-05-07 14:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("supermercado_app", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="prediccion",
            name="id",
        ),
        migrations.AlterField(
            model_name="prediccion",
            name="name",
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterModelTable(
            name="prediccion",
            table="tabla_predicciones",
        ),
    ]
