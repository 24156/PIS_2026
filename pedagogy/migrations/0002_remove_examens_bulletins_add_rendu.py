# Generated manually for PIS2026 refactor

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedagogy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RenduDevoir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='rendus/', verbose_name='Fichier rendu')),
                ('date_rendu', models.DateTimeField(auto_now_add=True, verbose_name='Date de rendu')),
                ('note', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Note')),
                ('commentaire', models.TextField(blank=True, verbose_name='Commentaire')),
                ('corrige_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rendus_corriges', to=settings.AUTH_USER_MODEL)),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rendus', to='academics.etudiant')),
                ('td', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rendus', to='pedagogy.travaildirige')),
                ('tp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rendus', to='pedagogy.travailpratique')),
            ],
            options={
                'verbose_name': 'Rendu de devoir',
                'verbose_name_plural': 'Rendus de devoirs',
                'ordering': ['-date_rendu'],
            },
        ),
        migrations.DeleteModel(name='Note'),
        migrations.DeleteModel(name='Bulletin'),
        migrations.DeleteModel(name='Examen'),
    ]
