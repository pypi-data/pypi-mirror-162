# Generated by Django 3.2.8 on 2021-10-29 12:12

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('m3_gar', '0004_auto_20211013_1106'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='addrobj',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectguid'], name='m3_gar_addr_objectg_b1f158_hash'),
        ),
        migrations.AddIndex(
            model_name='addrobj',
            index=django.contrib.postgres.indexes.BTreeIndex(fields=['isactive', 'isactual', 'level'], name='m3_gar_addr_isactiv_236c06_btree'),
        ),
        migrations.AddIndex(
            model_name='addrobjparams',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectid'], name='m3_gar_addr_objecti_335bbb_hash'),
        ),
        migrations.AddIndex(
            model_name='apartmentsparams',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectid'], name='m3_gar_apar_objecti_03b3f2_hash'),
        ),
        migrations.AddIndex(
            model_name='carplacesparams',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectid'], name='m3_gar_carp_objecti_12b2bc_hash'),
        ),
        migrations.AddIndex(
            model_name='housesparams',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectid'], name='m3_gar_hous_objecti_ad2270_hash'),
        ),
        migrations.AddIndex(
            model_name='reestrobjects',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectguid'], name='m3_gar_rees_objectg_281c48_hash'),
        ),
        migrations.AddIndex(
            model_name='roomsparams',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectid'], name='m3_gar_room_objecti_1f650d_hash'),
        ),
        migrations.AddIndex(
            model_name='steadsparams',
            index=django.contrib.postgres.indexes.HashIndex(fields=['objectid'], name='m3_gar_stea_objecti_66db3d_hash'),
        ),
    ]
