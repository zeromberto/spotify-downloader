# Generated by Django 2.0 on 2018-06-26 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=128, unique=True)),
                ('change_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]