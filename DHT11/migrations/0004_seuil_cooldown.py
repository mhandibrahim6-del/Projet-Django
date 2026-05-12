from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DHT11', '0003_seuil_ntfy'),
    ]

    operations = [
        migrations.AddField(
            model_name='seuil',
            name='derniere_alerte_temp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='seuil',
            name='derniere_alerte_humid',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
