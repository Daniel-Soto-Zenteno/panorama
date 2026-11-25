import json
from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, Client
from django.utils import timezone
from .models import Actividad, Comunidad, Lugar, Perfil, Publicacion, Comentario, Reporte, Asistencia, Auditoria
from .services import moderar, asistir, publicas


class FlujoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('organiza', 'organiza@example.invalid', 'Prueba-fuerte-762!')
        cls.other = User.objects.create_user('visitante', 'visitante@example.invalid', 'Prueba-fuerte-762!')
        cls.mod = User.objects.create_user('modera', 'modera@example.invalid', 'Prueba-fuerte-762!', is_staff=True)
        cls.c = Comunidad.objects.create(nombre='Cultura local', descripcion='Prueba', estado='APROBADO', autor=cls.owner)
        cls.l = Lugar.objects.create(nombre='Costanera', descripcion='Prueba', estado='APROBADO', autor=cls.owner, zona='puerto-montt', latitud=-41.47, longitud=-72.93)
        cls.start = timezone.now() + timedelta(days=5)
        cls.a = Actividad.objects.create(titulo='Encuentro cultural', descripcion='Datos ficticios', categoria='Cultura', zona=cls.l.zona, latitud=cls.l.latitud, longitud=cls.l.longitud, fecha_hora=cls.start, fin=cls.start+timedelta(hours=2), comunidad=cls.c, lugar=cls.l, creado_por=cls.owner, estado='APROBADO')

    def payload(self, **changes):
        d = {'titulo': 'Nuevo encuentro', 'descripcion': 'Actividad ficticia', 'categoria': 'Cultura', 'comunidad': self.c.pk, 'lugar': self.l.pk, 'fecha_hora': timezone.localtime(self.start).strftime('%Y-%m-%dT%H:%M'), 'fin': timezone.localtime(self.start+timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')}
        d.update(changes)
        return d

    def test_CP01_mapa_publico(self):
        """RF01: GET mapa y API sin sesión muestran el evento publicado."""
        self.assertContains(self.client.get('/'), self.a.titulo)
        self.assertEqual(len(self.client.get('/api/activities/').json()['activities']), 1)

    def test_CP02_ocultar_no_publicos_y_vencidos(self):
        """RF01 RF14: estados privados y fin vencido quedan fuera de API."""
        for estado in ['PENDIENTE', 'CANCELADO', 'FINALIZADO', 'RETIRADO', 'RECHAZADO']:
            self.a.estado = estado; self.a.save()
            self.assertEqual(self.client.get('/api/activities/').json()['activities'], [])
        self.a.estado='APROBADO'; self.a.fin=timezone.now()-timedelta(seconds=1); self.a.save()
        self.assertEqual(publicas().count(), 0)

    def test_CP03_filtros_combinados_y_vacio(self):
        """RF02: ciudad y categoría combinan AND; limpiar restaura resultados."""
        self.assertEqual(len(self.client.get('/api/activities/?zone=puerto-montt&category=Cultura').json()['activities']), 1)
        self.assertEqual(self.client.get('/api/activities/?zone=puerto-varas&category=Cultura').json()['activities'], [])
        self.assertContains(self.client.get('/?q=inexistente'), 'No encontramos')
        self.assertEqual(len(self.client.get('/api/activities/').json()['activities']), 1)

    def test_CP04_filtros_fecha_hora_invalidos(self):
        """RF02: fecha coincide; fecha u orden horario inválidos devuelven 400."""
        day = timezone.localtime(self.start).date().isoformat()
        self.assertEqual(len(self.client.get('/api/activities/', {'date':day}).json()['activities']), 1)
        for args in [{'date':'2026-99-99'}, {'from':'xx'}, {'from':'19:00','to':'10:00'}]:
            self.assertEqual(self.client.get('/api/activities/', args).status_code, 400)

    def test_CP05_ficha_comunidad_y_privacidad(self):
        """RF03 RNF02: ficha corresponde al registro; API omite correo y clave."""
        response=self.client.get(f'/activity/{self.a.pk}/')
        self.assertContains(response,self.c.nombre)
        self.assertNotContains(response,self.owner.email)
        raw=self.client.get('/api/activities/').content.decode()
        self.assertNotIn('password',raw); self.assertNotIn(self.owner.email,raw)

    def test_CP06_registro_correo_unico(self):
        """RF04: nueva cuenta persiste; correo repetido se rechaza."""
        data={'username':'nueva','email':'NUEVA@example.invalid','password1':'Clave-segura-739!','password2':'Clave-segura-739!','consentimiento':'on'}
        self.assertEqual(self.client.post('/account/register/',data).status_code,302)
        self.assertTrue(User.objects.filter(username='nueva').exists())
        self.client.post('/logout/'); data['username']='duplicada'
        self.assertContains(self.client.post('/account/register/',data),'ya está registrado')
        self.assertFalse(User.objects.filter(username='duplicada').exists())

    def test_CP07_login_logout_y_credenciales(self):
        """RF04: login válido, clave inválida y cierre que bloquea escrituras."""
        self.assertEqual(self.client.post('/api/login/',json.dumps({'username':'organiza','password':'incorrecta'}),content_type='application/json').status_code,401)
        r=self.client.post('/api/login/',json.dumps({'username':'organiza','password':'Prueba-fuerte-762!'}),content_type='application/json')
        self.assertEqual(r.status_code,200); self.assertTrue(r.json()['authenticated'])
        self.client.post('/logout/')
        self.assertEqual(self.client.post('/propose/actividad/',self.payload()).status_code,302)
        self.assertEqual(Actividad.objects.count(),1)

    def test_CP08_perfil_solo_propio(self):
        """RF05: un ID ajeno en POST no cambia el perfil ajeno."""
        p=Perfil.objects.create(usuario=self.other,nombre='Original')
        self.client.force_login(self.owner)
        self.client.post('/profile/',{'nombre':'Nuevo nombre','descripcion':'Bio','intereses':'Cultura','usuario':self.other.pk})
        p.refresh_from_db(); self.assertEqual(p.nombre,'Original')
        self.assertEqual(Perfil.objects.get(usuario=self.owner).nombre,'Nuevo nombre')

    def test_CP09_propuestas_y_coordenadas(self):
        """RF06: comunidad queda pendiente y coordenadas inválidas no crean lugar."""
        self.client.force_login(self.owner)
        self.client.post('/propose/comunidad/',{'nombre':'Nueva comunidad','descripcion':'Cultura'})
        self.assertTrue(Comunidad.objects.filter(nombre='Nueva comunidad',estado='PENDIENTE').exists())
        r=self.client.post('/propose/lugar/',{'nombre':'Mal','descripcion':'Prueba','zona':'puerto-montt','latitud':99,'longitud':-72})
        self.assertEqual(r.status_code,200); self.assertEqual(Lugar.objects.count(),1)

    def test_CP10_flujo_propuesta_aprobacion_asistencia(self):
        """RF07 RF08 RF12: propuesta→oculta→aprobada→visible→asistencia persistida."""
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post('/propose/actividad/',self.payload()).status_code,302)
        a=Actividad.objects.get(titulo='Nuevo encuentro')
        self.assertEqual(a.estado,'PENDIENTE'); self.assertFalse(publicas().filter(pk=a.pk).exists())
        self.client.force_login(self.mod)
        self.client.post(f'/moderation/actividad/{a.pk}/',{'motivo':'Datos revisados','decision':'APROBADO'})
        self.assertTrue(publicas().filter(pk=a.pk).exists())
        self.client.force_login(self.other); self.client.post(f'/activity/{a.pk}/rsvp/')
        self.assertTrue(Asistencia.objects.filter(actividad=a,usuario=self.other).exists())
        self.assertTrue(Auditoria.objects.filter(objeto_id=a.pk,decision='APROBADO').exists())

    def test_CP11_evento_invalido_y_referencia(self):
        """RF07 RNF06: fin anterior y FK inexistente rechazan el envío sin cambios."""
        self.client.force_login(self.owner)
        for payload in [self.payload(fin='2000-01-01T10:00'),self.payload(comunidad=999999),self.payload(descripcion='')]:
            self.assertEqual(self.client.post('/propose/actividad/',payload).status_code,200)
        self.assertEqual(Actividad.objects.count(),1)

    def test_CP12_rsvp_idempotente_cancelacion(self):
        """RF08: dos confirmaciones mantienen una fila y cancelar deja cero."""
        self.assertEqual(asistir(self.other,self.a.pk),1);self.assertEqual(asistir(self.other,self.a.pk),1)
        self.assertEqual(asistir(self.other,self.a.pk,True),0)

    def test_CP13_rsvp_iniciado_o_cancelado(self):
        """RF08 RF14: rechaza evento iniciado y cancelado."""
        self.a.fecha_hora=timezone.now()-timedelta(minutes=1);self.a.save()
        with self.assertRaises(ValidationError): asistir(self.other,self.a.pk)
        self.a.estado='CANCELADO';self.a.save()
        with self.assertRaises(ValidationError): asistir(self.other,self.a.pk)

    def test_CP14_publicacion_y_comentario(self):
        """RF09 RF10: texto persiste con autor y relación de origen."""
        self.client.force_login(self.other)
        self.client.post(f'/community/{self.c.pk}/',{'texto':'Hola comunidad'})
        p=Publicacion.objects.get(texto='Hola comunidad')
        self.client.post(f'/post/{p.pk}/comment/',{'texto':'Nos vemos'})
        self.assertEqual(p.autor,self.other);self.assertEqual(p.comentarios.get().texto,'Nos vemos')

    def test_CP15_vacios_y_publicacion_retirada(self):
        """RF09 RF10: rechaza texto vacío y respuesta a publicación retirada."""
        self.client.force_login(self.other);self.client.post(f'/community/{self.c.pk}/',{'texto':'   '})
        self.assertEqual(Publicacion.objects.count(),0)
        p=Publicacion.objects.create(comunidad=self.c,autor=self.owner,texto='Retirado',estado='RETIRADO')
        self.assertEqual(self.client.post(f'/post/{p.pk}/comment/',{'texto':'Respuesta'}).status_code,404)
        self.assertEqual(Comentario.objects.count(),0)

    def test_CP16_reporte_no_oculta(self):
        """RF11: crea reporte abierto sin retirar evento."""
        self.client.force_login(self.other);self.client.post(f'/report/actividad/{self.a.pk}/',{'motivo':'Revisar información'})
        self.assertEqual(Reporte.objects.get().estado,'ABIERTO');self.assertTrue(publicas().filter(pk=self.a.pk).exists())

    def test_CP17_roles_moderacion(self):
        """RF12 RNF01: usuario común no modera ni administra distintivos."""
        self.client.force_login(self.other)
        for url in ['/moderation/',f'/moderation/actividad/{self.a.pk}/',f'/activity/{self.a.pk}/badge/']:
            self.assertEqual(self.client.post(url,{'decision':'RETIRADO','motivo':'Intento indebido'}).status_code,403)
        self.a.refresh_from_db();self.assertEqual(self.a.estado,'APROBADO')

    def test_CP18_auditoria_atomica(self):
        """RF12 RNF06: si falla auditoría la transacción revierte el retiro."""
        with patch('core.services.Auditoria.objects.create',side_effect=RuntimeError('Fallo simulado')):
            with self.assertRaises(RuntimeError): moderar(self.mod,'actividad',self.a.pk,'RETIRADO','Prueba transaccional')
        self.a.refresh_from_db();self.assertEqual(self.a.estado,'APROBADO');self.assertEqual(Auditoria.objects.count(),0)

    def test_CP19_cierre_reporte(self):
        """RF13: cierre guarda responsable y fecha y conserva evento público."""
        r=Reporte.objects.create(tipo='actividad',objeto_id=self.a.pk,autor=self.other,motivo='Revisar')
        self.client.force_login(self.mod);self.client.post(f'/resolve/{r.pk}/',{'motivo':'No corresponde retirar'})
        r.refresh_from_db();self.assertEqual(r.estado,'CERRADO');self.assertEqual(r.responsable,self.mod);self.assertIsNotNone(r.resuelto_en)
        self.assertTrue(publicas().filter(pk=self.a.pk).exists())

    def test_CP20_edicion_ajena_y_nueva_revision(self):
        """RF14: deniega editar ajeno; cambio de fecha propio vuelve a pendiente."""
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(f'/activity/{self.a.pk}/edit/',self.payload()).status_code,404)
        self.client.force_login(self.owner)
        self.client.post(f'/activity/{self.a.pk}/edit/',self.payload(fecha_hora=timezone.localtime(self.start+timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M')))
        self.a.refresh_from_db();self.assertEqual(self.a.estado,'PENDIENTE')

    def test_CP21_cancelar_y_finalizar(self):
        """RF14: cancelación propia oculta y comando finaliza vencidos."""
        from django.core.management import call_command
        self.client.force_login(self.owner);self.client.post(f'/activity/{self.a.pk}/cancel/')
        self.assertFalse(publicas().exists())
        self.a.estado='APROBADO';self.a.fin=timezone.now()-timedelta(seconds=1);self.a.save()
        call_command('finalizar_eventos',verbosity=0)
        self.a.refresh_from_db();self.assertEqual(self.a.estado,'FINALIZADO')

    def test_CP22_distintivos_simulados(self):
        """RF15: moderador activa banderas y ficha indica simulación."""
        self.client.force_login(self.mod);self.client.post(f'/activity/{self.a.pk}/badge/')
        self.a.refresh_from_db();self.assertTrue(self.a.destacado)
        self.client.post(f'/activity/{self.a.pk}/badge/', {'target':'organizador'})
        self.assertTrue(Perfil.objects.get(usuario=self.owner).verificado)
        self.client.post(f'/activity/{self.a.pk}/badge/', {'target':'evento'})
        self.assertTrue(Perfil.objects.get(usuario=self.owner).verificado)
        self.client.post(f'/activity/{self.a.pk}/badge/', {'target':'evento'})
        self.assertContains(self.client.get(f'/activity/{self.a.pk}/'),'Destacado simulado')

    def test_CP23_metricas_privadas(self):
        """RF16: apertura suma acceso y lista propia excluye eventos ajenos."""
        self.client.get(f'/activity/{self.a.pk}/');self.a.refresh_from_db();self.assertEqual(self.a.aperturas,1)
        self.client.force_login(self.other);self.assertNotContains(self.client.get('/mine/'),self.a.titulo)

    def test_CP24_csrf_y_metodos(self):
        """RNF01: POST sin CSRF devuelve 403 y GET logout devuelve 405."""
        c=Client(enforce_csrf_checks=True);c.force_login(self.owner)
        self.assertEqual(c.post('/propose/actividad/',self.payload()).status_code,403)
        self.assertEqual(c.get('/logout/').status_code,405)

    def test_CP25_hash_y_xss(self):
        """RNF02: clave con hash y texto malicioso escapado en foro."""
        self.assertNotEqual(self.owner.password,'Prueba-fuerte-762!');self.assertTrue(self.owner.check_password('Prueba-fuerte-762!'))
        Publicacion.objects.create(comunidad=self.c,autor=self.owner,texto='<script>alert(1)</script>')
        r=self.client.get(f'/community/{self.c.pk}/')
        self.assertNotContains(r,'<script>alert(1)</script>');self.assertContains(r,'&lt;script&gt;')

    def test_CP26_unicidad_base_datos(self):
        """RNF06: restricción impide RSVP duplicado incluso sin pasar por servicio."""
        Asistencia.objects.create(usuario=self.other,actividad=self.a)
        with self.assertRaises(IntegrityError),transaction.atomic():
            Asistencia.objects.create(usuario=self.other,actividad=self.a)

    def test_CP27_correo_unico_base_datos(self):
        """RF04 RNF06: índice ignora mayúsculas y protege carreras."""
        with self.assertRaises(IntegrityError),transaction.atomic():
            User.objects.create_user('duplicada','ORGANIZA@example.invalid','Otra-clave-892!')

    def test_CP28_retiro_comunidad_oculta_hijos(self):
        """RF12: retirar comunidad oculta eventos y foro al público."""
        moderar(self.mod,'comunidad',self.c.pk,'RETIRADO','Prueba de retiro')
        self.assertFalse(publicas().exists());self.assertEqual(self.client.get(f'/community/{self.c.pk}/').status_code,404)
