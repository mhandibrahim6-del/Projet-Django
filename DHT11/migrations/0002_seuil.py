from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DHT11', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seuil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_max', models.FloatField(default=30.0)),
                ('humidite_max', models.FloatField(default=80.0)),
                ('telephone', models.CharField(default='', max_length=20)),
                ('apikey', models.CharField(default='', max_length=50)),
            ],
        ),
    ]
