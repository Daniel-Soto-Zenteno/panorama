"""Contratos de comunidades, moderación y fotografías opcionales."""
import io
import json
import tempfile
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from .models import Actividad, Comunidad


class CommunityFlowTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(username='author')
        self.other = get_user_model().objects.create_user(username='other')
        self.mod = get_user_model().objects.create_user(username='moderator', is_staff=True)
        self.group = Comunidad.objects.create(nombre='Deportes locales', categoria='Deportes', aprobado=True)
        self.payload = dict(title='Partido en el barrio', description='Trae agua', category='Deportes', zone='puerto-montt', lat=-41.47, lng=-72.93, community_id=self.group.id, all_year=True)
        self.client.force_login(self.author)

    def send(self, method, url, data):
        return getattr(self.client, method)(url, data=json.dumps(data), content_type='application/json')

    def test_pending_post_then_moderation_and_persistent_comment(self):
        data = dict(self.payload, featured=True, status='published')
        r = self.send('post', '/api/activities/', data)
        self.assertEqual(r.status_code, 201)
        a = r.json()['activity']
        self.assertEqual(a['status'], 'pending')
        self.assertFalse(a['featured'])
        self.assertIsNone(a['image_url'])
        self.assertEqual(a['community_name'], self.group.nombre)
        self.assertEqual(Client().get('/api/activities/').json()['activities'], [])
        self.assertEqual(Client().get(f"/api/activities/{a['id']}/comments/").status_code, 404)
        self.client.force_login(self.other)
        self.assertEqual(self.send('patch', f"/api/activities/{a['id']}/", {'title':'Cambio ajeno'}).status_code, 403)
        self.client.force_login(self.mod)
        self.assertEqual(self.send('patch', f"/api/activities/{a['id']}/", {'status':'published', 'featured':True}).status_code, 200)
        public = Client().get('/api/activities/').json()['activities']
        self.assertTrue(public[0]['featured'])
        self.client.force_login(self.other)
        r = self.send('post', f"/api/activities/{a['id']}/comments/", {'text':'¿Dónde nos reunimos?'})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Client().get(f"/api/activities/{a['id']}/comments/").json()['comments'][0]['text'], '¿Dónde nos reunimos?')
        self.client.force_login(self.author)
        self.send('patch', f"/api/activities/{a['id']}/", {'description':'Lugar actualizado'})
        self.assertEqual(Client().get('/api/activities/').json()['activities'], [])

    def test_independent_and_community_posts_are_separate(self):
        independent = dict(self.payload, title='Paseo independiente', community_id=None)
        self.assertIsNone(self.send('post','/api/activities/',independent).json()['activity']['community_id'])
        self.send('post','/api/activities/',self.payload)
        groups = self.client.get('/api/communities/').json()['communities']
        self.assertEqual(groups[0]['posts_count'], 1)
        self.assertEqual(self.send('post','/api/activities/',dict(self.payload, category='Cultura')).status_code,400)
        self.assertEqual(self.send('post','/api/activities/',dict(self.payload, community_id=9999)).status_code,400)

    def test_community_needs_moderation(self):
        r = self.send('post', '/api/communities/', {'name':'Ciclismo local','category':'Deportes','description':'Salidas y conversación'})
        self.assertEqual(r.status_code,201)
        self.assertFalse(r.json()['community']['approved'])
        cid = r.json()['community']['id']
        self.assertNotIn(cid,[c['id'] for c in Client().get('/api/communities/').json()['communities']])
        self.assertEqual(self.send('post',f'/api/communities/{cid}/moderate/',{'approved':True}).status_code,403)
        self.client.force_login(self.mod)
        self.assertEqual(self.send('post',f'/api/communities/{cid}/moderate/',{'approved':True}).status_code,200)
        self.assertIn(cid,[c['id'] for c in Client().get('/api/communities/').json()['communities']])

    def test_image_is_optional_and_upload_is_validated(self):
        aid=self.send('post','/api/activities/',self.payload).json()['activity']['id']
        endpoint=f'/api/activities/{aid}/image/'
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            bad=SimpleUploadedFile('bad.svg',b'<svg onload="alert(1)"></svg>',content_type='image/svg+xml')
            self.assertEqual(self.client.post(endpoint,{'image':bad}).status_code,400)
            output=io.BytesIO();Image.new('RGB',(50,50),'green').save(output,'PNG')
            good=SimpleUploadedFile('photo.png',output.getvalue(),content_type='image/png')
            result=self.client.post(endpoint,{'image':good})
            self.assertEqual(result.status_code,200)
            self.assertIn('/api/activities/', result.json()['activity']['image_url'])
            self.assertEqual(Client().get(result.json()['activity']['image_url']).status_code,404)
            activity=Actividad.objects.get(pk=aid)
            with Image.open(activity.imagen.path) as image:
                self.assertEqual(image.format,'JPEG')
            self.client.force_login(self.other)
            self.assertEqual(self.client.post(endpoint,{}).status_code,403)

    def test_registration_and_password_validation(self):
        self.client.logout()
        self.assertEqual(self.send('post','/api/register/',{'username':'newuser','password':'123'}).status_code,400)
        r=self.send('post','/api/register/',{'username':'newuser','password':'uncommon-C93!x47'})
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.json()['authenticated'])
        self.assertFalse(r.json()['is_admin'])
        self.assertTrue(get_user_model().objects.get(username='newuser').check_password('uncommon-C93!x47'))
