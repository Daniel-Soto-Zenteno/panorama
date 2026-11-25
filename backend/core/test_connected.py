"""Pruebas de integración: cuentas, aislamiento de datos y moderación real."""
import io
import json
import tempfile
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from .models import Actividad, Comunidad, Guardado, Perfil, Reporte


class ConnectedAppTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.author = users.objects.create_user(username='autor', password='temporary-Secret9!')
        self.other = users.objects.create_user(username='lector', password='temporary-Secret8!')
        self.mod = users.objects.create_user(username='moderador', is_staff=True)
        self.group = Comunidad.objects.create(nombre='Deportes', categoria='Deportes', aprobado=True)
        self.post = Actividad.objects.create(titulo='Punto de encuentro', creado_por=self.author, comunidad=self.group, latitud=-41.47, longitud=-72.94, categoria='Deportes', todo_el_ano=True)
        self.client.force_login(self.author)

    def request(self, method, url, data):
        return getattr(self.client, method)(url, data=json.dumps(data), content_type='application/json')

    def test_profile_persists_and_cannot_change_roles_or_username(self):
        result=self.request('patch','/api/profile/',{'name':'Nombre visible','bio':'Me gusta pedalear','is_admin':True,'username':'otro'})
        self.assertEqual(result.status_code,200)
        self.assertFalse(result.json()['is_admin'])
        self.assertEqual(result.json()['username'],'autor')
        fresh=Client();fresh.force_login(self.author)
        self.assertEqual(fresh.get('/api/session/').json()['display_name'],'Nombre visible')
        self.assertEqual(fresh.get('/api/profile/').json()['bio'],'Me gusta pedalear')
        fresh.force_login(self.other)
        self.assertNotEqual(fresh.get('/api/profile/').json()['display_name'],'Nombre visible')
        self.assertEqual(Client().get('/api/profile/').status_code,401)
        self.assertEqual(self.request('patch','/api/profile/',{'name':'x'}).status_code,400)

    def test_saved_posts_are_per_account_idempotent_and_persistent(self):
        endpoint=f'/api/saved/{self.post.id}/'
        for _ in range(2):
            self.assertEqual(self.client.post(endpoint).status_code,200)
        self.assertEqual(Guardado.objects.count(),1)
        fresh=Client();fresh.force_login(self.author)
        self.assertEqual(fresh.get('/api/saved/').json()['saved'],[self.post.id])
        fresh.force_login(self.other)
        self.assertEqual(fresh.get('/api/saved/').json()['saved'],[])
        self.assertEqual(Client().get('/api/saved/').status_code,401)
        self.assertEqual(self.client.delete(endpoint).status_code,200)
        self.assertEqual(Guardado.objects.count(),0)

    def test_private_image_becomes_public_only_after_approval(self):
        self.post.estado='pending';self.post.save()
        with tempfile.TemporaryDirectory() as directory,override_settings(MEDIA_ROOT=directory):
            buffer=io.BytesIO();Image.new('RGB',(30,20),'green').save(buffer,'PNG')
            result=self.client.post(f'/api/activities/{self.post.id}/image/',{'image':SimpleUploadedFile('foto.png',buffer.getvalue(),content_type='image/png')})
            self.assertEqual(result.status_code,200)
            url=result.json()['activity']['image_url']
            self.assertEqual(Client().get(url).status_code,404)
            self.client.force_login(self.other)
            self.assertEqual(self.client.get(url).status_code,404)
            self.client.force_login(self.mod)
            response=self.client.get(url);self.assertEqual(response.status_code,200);response.close()
            self.request('patch',f'/api/activities/{self.post.id}/',{'status':'published'})
            response=Client().get(url);self.assertEqual(response.status_code,200)
            self.assertEqual(response['Content-Type'],'image/jpeg');response.close()
            self.client.force_login(self.author)
            result=self.request('patch',f'/api/activities/{self.post.id}/',{'remove_image':True})
            self.assertIsNone(result.json()['activity']['image_url'])
            self.assertEqual(Client().get(url).status_code,404)

    def test_reports_require_account_and_only_moderator_can_read_or_resolve(self):
        payload={'post_id':self.post.id,'reason':'Datos personales','text':'Revisar esta publicación'}
        self.assertEqual(Client().post('/api/reports/',data=json.dumps(payload),content_type='application/json').status_code,401)
        result=self.request('post','/api/reports/',payload)
        self.assertEqual(result.status_code,201)
        rid=result.json()['id']
        self.assertEqual(self.client.get('/api/reports/').status_code,403)
        self.assertEqual(self.request('patch',f'/api/reports/{rid}/',{'resolved':True}).status_code,403)
        self.client.force_login(self.mod)
        self.assertEqual(self.client.get('/api/reports/').json()['reports'][0]['reason'],'Datos personales')
        self.assertEqual(self.request('patch',f'/api/reports/{rid}/',{'resolved':True}).status_code,200)
        self.assertEqual(self.client.get('/api/reports/').json()['reports'],[])
        self.assertTrue(Reporte.objects.get(pk=rid).resuelto)

    def test_owner_sees_rejected_community_but_public_does_not(self):
        self.client.force_login(self.other)
        proposal=self.request('post','/api/communities/',{'name':'Paseos tranquilos','category':'Aire libre','description':'Rutas para caminar'})
        cid=proposal.json()['community']['id']
        self.assertIn(cid,[c['id'] for c in self.client.get('/api/communities/').json()['communities']])
        self.assertNotIn(cid,[c['id'] for c in Client().get('/api/communities/').json()['communities']])
        self.client.force_login(self.mod)
        self.request('post',f'/api/communities/{cid}/moderate/',{'approved':False,'rejected':True})
        self.client.force_login(self.other)
        c=next(c for c in self.client.get('/api/communities/').json()['communities'] if c['id']==cid)
        self.assertTrue(c['rejected']);self.assertFalse(c['approved'])

    def test_pace_and_coordinates_are_validated_and_comments_keep_display_name(self):
        self.assertEqual(self.request('patch',f'/api/activities/{self.post.id}/',{'pace':'calm','place':'Costanera'}).status_code,200)
        self.assertEqual(self.request('patch',f'/api/activities/{self.post.id}/',{'pace':'unknown'}).status_code,400)
        self.assertEqual(self.request('patch',f'/api/activities/{self.post.id}/',{'lat':float('nan')}).status_code,400)
        self.request('patch','/api/profile/',{'name':'Cami','bio':''})
        self.request('post',f'/api/activities/{self.post.id}/comments/',{'text':'Información útil'})
        c=self.client.get(f'/api/activities/{self.post.id}/comments/').json()['comments'][0]
        self.assertEqual(c['display_name'],'Cami');self.assertTrue(c['can_delete'])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/api/activities/{self.post.id}/comments/').status_code,404)

    def test_new_write_endpoints_reject_missing_csrf(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.author)
        self.assertEqual(client.patch('/api/profile/',data='{}',content_type='application/json').status_code,403)
        self.assertEqual(client.post(f'/api/saved/{self.post.id}/').status_code,403)
        self.assertEqual(client.post('/api/reports/',data='{}',content_type='application/json').status_code,403)
    def test_recurring_activity_and_meeting_place_remain_distinct(self):
        recurring=self.request('patch',f'/api/activities/{self.post.id}/',{'kind':'event','all_year':True,'schedule':'Sábados de 11:00 a 13:00'})
        self.assertEqual(recurring.status_code,200)
        self.assertEqual(recurring.json()['activity']['kind'],'event')
        self.assertTrue(recurring.json()['activity']['all_year'])
        self.assertIsNone(Actividad.objects.get(pk=self.post.id).fecha_hora)
        self.assertEqual(self.request('patch',f'/api/activities/{self.post.id}/',{'kind':'place','all_year':False}).status_code,400)
        place=self.request('patch',f'/api/activities/{self.post.id}/',{'kind':'place','all_year':True,'schedule':'Durante el día'})
        self.assertEqual(place.status_code,200)
        self.assertEqual(place.json()['activity']['kind'],'place')
