# Generated by Django 3.2.4 on 2022-06-01 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m3_gar', '0014_addrobj_name_with_typename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='normativedocs',
            name='orgname',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Наименование органа создвшего нормативный документ'),
        ),
    ]
