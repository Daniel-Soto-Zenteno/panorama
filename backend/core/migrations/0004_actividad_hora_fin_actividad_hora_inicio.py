from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0003_actividad_aperturas_actividad_estado_actividad_fin_and_more')]
    operations = [migrations.AddField('actividad', 'hora_fin', models.TimeField(blank=True, null=True)), migrations.AddField('actividad', 'hora_inicio', models.TimeField(blank=True, null=True))]
