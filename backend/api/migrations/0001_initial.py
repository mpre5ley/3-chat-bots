# Django instructions to generate db tables
from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True
    dependencies = []

    # Create database tables
    operations = [
        migrations.CreateModel(
            name='ModelResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('model_name', models.CharField(max_length=100)),
                ('model_id', models.CharField(max_length=100)),
                ('response', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PromptSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('responses', models.ManyToManyField(related_name='sessions', to='api.modelresponse')),
            ],
            options={'ordering': ['-created_at'],
            },
        ),
    ]