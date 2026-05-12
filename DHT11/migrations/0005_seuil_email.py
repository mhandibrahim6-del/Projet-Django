from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DHT11', '0004_seuil_cooldown'),
    ]

    operations = [
        migrations.RemoveField(model_name='seuil', name='topic'),
        migrations.AddField(
            model_name='seuil',
            name='email_from',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='seuil',
            name='email_password',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='seuil',
            name='email_to',
            field=models.CharField(default='', max_length=100),
        ),
    ]
