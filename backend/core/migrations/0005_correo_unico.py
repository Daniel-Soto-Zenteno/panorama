from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core', '0004_actividad_hora_fin_actividad_hora_inicio')]
    operations = [migrations.RunSQL(
        "CREATE UNIQUE INDEX panorama_correo_unico ON auth_user (LOWER(email)) WHERE email <> ''",
        'DROP INDEX panorama_correo_unico',
    )]
