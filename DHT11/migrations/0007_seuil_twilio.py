from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DHT11', '0006_alter_seuil_options'),
    ]

    operations = [
        migrations.RemoveField(model_name='seuil', name='email_from'),
        migrations.RemoveField(model_name='seuil', name='email_password'),
        migrations.RemoveField(model_name='seuil', name='email_to'),
        migrations.AddField(
            model_name='seuil',
            name='twilio_sid',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='seuil',
            name='twilio_token',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='seuil',
            name='whatsapp_to',
            field=models.CharField(default='', max_length=20),
        ),
    ]
