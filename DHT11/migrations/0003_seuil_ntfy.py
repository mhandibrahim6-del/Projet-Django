from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DHT11', '0002_seuil'),
    ]

    operations = [
        migrations.RemoveField(model_name='seuil', name='telephone'),
        migrations.RemoveField(model_name='seuil', name='apikey'),
        migrations.AddField(
            model_name='seuil',
            name='topic',
            field=models.CharField(default='', max_length=100),
        ),
    ]
