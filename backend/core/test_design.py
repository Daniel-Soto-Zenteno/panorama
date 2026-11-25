"""Prueba de integración del contrato que utiliza la nueva interfaz."""
import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class DesignIntegrationTests(TestCase):
    def test_session_csrf_admin_crud_and_public_filters(self):
        user = get_user_model().objects.create_user(username='design-test', password='temporary-test-only', is_staff=True)
        client = Client(enforce_csrf_checks=True)
        old_token = client.get('/api/csrf/').json()['csrfToken']
        response = client.post('/api/login/', data=json.dumps({'username':user.username,'password':'temporary-test-only'}), content_type='application/json', HTTP_X_CSRFTOKEN=old_token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_admin'])
        payload = dict(title='Prueba de interfaz', category='Cultura', zone='puerto-varas', lat=-41.32,lng=-72.98,all_year=True,schedule='10:00 a 17:00')
        self.assertEqual(client.post('/api/activities/', data=json.dumps(payload),content_type='application/json',HTTP_X_CSRFTOKEN=old_token).status_code,403)
        new_token=client.get('/api/csrf/').json()['csrfToken']
        created=client.post('/api/activities/',data=json.dumps(payload),content_type='application/json',HTTP_X_CSRFTOKEN=new_token)
        self.assertEqual(created.status_code,201)
        activity_id=created.json()['activity']['id']
        self.assertEqual(len(Client().get('/api/activities/?zone=puerto-varas&category=Cultura').json()['activities']),1)
        self.assertEqual(len(Client().get('/api/activities/?zone=puerto-montt').json()['activities']),0)
        edited=client.patch(f'/api/activities/{activity_id}/',data=json.dumps({'title':'Título actualizado'}),content_type='application/json',HTTP_X_CSRFTOKEN=new_token)
        self.assertEqual(edited.json()['activity']['title'],'Título actualizado')
        self.assertEqual(client.delete(f'/api/activities/{activity_id}/',HTTP_X_CSRFTOKEN=new_token).status_code,200)
        self.assertEqual(client.post('/api/logout/',HTTP_X_CSRFTOKEN=new_token).status_code,200)

    def test_guest_cannot_create_and_regular_user_must_provide_valid_post(self):
        self.assertEqual(self.client.post('/api/activities/',data='{}',content_type='application/json').status_code,401)
        user=get_user_model().objects.create_user(username='visitor-test')
        self.client.force_login(user)
        self.assertEqual(self.client.post('/api/activities/',data='{}',content_type='application/json').status_code,400)

    def test_conversation_persists_and_requires_account(self):
        from .models import Actividad, Conversacion
        activity=Actividad.objects.create(titulo='Actividad de prueba',latitud=-41.4,longitud=-72.9)
        endpoint=f'/api/activities/{activity.id}/comments/'
        self.assertEqual(self.client.get(endpoint).json()['comments'],[])
        self.assertEqual(self.client.post(endpoint,data=json.dumps({'text':'Hola'}),content_type='application/json').status_code,401)
        user=get_user_model().objects.create_user(username='commenter')
        self.client.force_login(user)
        for invalid in ['', '   ', 'a'*2001, None]:
            self.assertEqual(self.client.post(endpoint,data=json.dumps({'text':invalid}),content_type='application/json').status_code,400)
        text='<img src=x onerror=alert(1)> pregunta de prueba'
        response=self.client.post(endpoint,data=json.dumps({'text':text}),content_type='application/json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(Conversacion.objects.get().texto,text)
        self.assertEqual(Client().get(endpoint).json()['comments'][0]['author'],'commenter')
        self.assertEqual(Client().get('/api/activities/').json()['activities'][0]['comments_count'],1)
        self.assertEqual(self.client.get('/api/activities/999999/comments/').status_code,404)

    def test_only_author_or_moderator_can_remove_comment(self):
        from .models import Actividad, Conversacion
        activity=Actividad.objects.create(titulo='Prueba',latitud=-41.4,longitud=-72.9)
        author=get_user_model().objects.create_user(username='author')
        outsider=get_user_model().objects.create_user(username='outsider')
        admin=get_user_model().objects.create_user(username='moderator',is_staff=True)
        comment=Conversacion.objects.create(actividad=activity,autor=author,texto='Hola')
        endpoint=f'/api/comments/{comment.id}/'
        self.assertEqual(self.client.delete(endpoint).status_code,401)
        self.client.force_login(outsider)
        self.assertEqual(self.client.delete(endpoint).status_code,403)
        self.client.force_login(admin)
        self.assertEqual(self.client.delete(endpoint).status_code,200)
        self.assertFalse(Conversacion.objects.filter(pk=comment.id).exists())
