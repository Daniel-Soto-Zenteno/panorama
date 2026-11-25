# Validación de la integración

## Automatizada

17 pruebas de Django pasaron con SQLite. Se cubren sesión y rotación CSRF, registro y validación de contraseña, propuestas y moderación, comunidades, autoría, comentarios persistentes, perfiles por cuenta, guardados idempotentes y aislados, reportes exclusivos de moderador, validación de coordenadas y ritmo, actividades recurrentes y lugares de encuentro, imágenes válidas/inválidas y privacidad de imágenes pendientes. Se comprobó Django y que no haya cambios de modelos pendientes de migración. Sintaxis JavaScript verificada con Node.

La suite usa bases y directorios temporales. No depende de los ejemplos del entorno local ni de cuentas predefinidas.

## Navegador

1. Escritorio: registro, creación de propuesta con punto elegido en el mapa, edición de perfil, comentario y guardado persistidos. Evidencia REA ev_17eedb9d00bd0f3745985131236d19e9167ca8b6d4d20a5e6881c5d05248971e. Sin page-errors.
2. Nueva sesión móvil a 390 × 844: acceso a la misma cuenta, recuperación del nombre visible, biografía, post, comentario y guardado; creación de comunidad pendiente. Evidencia ev_ac6ba6f8afc99d65325e6ed58d028e8ceb2de99e9585e8379835ae9b2b3ab228. Sin page-errors.
3. Moderador: se aprobó y destacó la propuesta y se envió un reporte; la cola se observó en ev_380a1af3243709b34341a63743185a6c6df3199567140fe041e5fa3aaae2c927. Sin page-errors en esa observación.
4. Moderador: resolución del reporte y aprobación de la comunidad; cola sin propuestas pendientes al finalizar. Evidencia ev_7a4cc193f93b61061979799a05c540b93ea1f5b9b32e94ba1983143b9a90dc75. Sin page-errors.

Un escenario largo de moderación se interrumpió tras enviar el reporte. Se comprobó el resto mediante los escenarios acotados 3 y 4, sin interpretar la interrupción como una validación completa.

Las cuentas, post, comentario, guardado, reporte y comunidad temporales se eliminaron al finalizar. Permanecen los siete ejemplos anteriores, identificados como ficticios; no se suben a GitHub porque la base local está ignorada.

## Límites

La base PostgreSQL original está configurada pero no se probó una conexión a una instancia real. No se realizó despliegue público. La subida y privacidad de imágenes se probaron en el servidor; no se automatizó un selector de archivos con una fotografía real del usuario. El mapa depende de servicios externos y necesita internet.

Para repetir: .venv/Scripts/python.exe backend/manage.py test core --settings=config.settings_local.
