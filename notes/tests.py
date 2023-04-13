from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import User, Note


class UserTests(APITestCase):
    def setUp(self) -> None:
        self.username = 'test'
        self.email = 'test@icloud.com'
        self.password = 'test123'
    
    def create_user(self) -> User:
        user = User(
            email=self.email,
            username=self.username
        )
        user.set_password(self.password)
        user.save()

        return user

    def test_register_user(self):
        url = reverse('register')
        data = {
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'password2': self.password
        }
        response = self.client.post(
            path=url,
            data=data,
            format='json'
        )
        user = User.objects.get(username=self.username, email=self.email)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)

    def test_authorization(self):
        user = self.create_user()
        url = reverse('token_obtain_pair')
        data = {
            'email': self.email,
            'password': self.password
        }
        response = self.client.post(
            path=url,
            data=data,
            format='json'
        )
        callback_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tuple(callback_data.keys()), ('refresh', 'access'))


class TestNoteViewSet(APITestCase):
    def setUp(self) -> None:
        self.username = 'test'
        self.email = 'test@icloud.com'
        self.password = 'test123'
        self.text = 'test text'
        self.title = 'test title'

    def create_user(self) -> User:
        user = User(
            email=self.email,
            username=self.username
        )
        user.set_password(self.password)
        user.save()

        return user

    def create_note(self, user_id: int) -> Note:
        note = Note.objects.create(
            title=self.title,
            text=self.text,
            user_id=user_id
        )

        return note

    def test_note_list(self):
        user = self.create_user()
        note = self.create_note(user.pk)
        url = reverse('token_obtain_pair')
        data = {
            'email': self.email,
            'password': self.password
        }
        response = self.client.post(
            path=url,
            data=data,
            format='json'
        )
        refresh_token, access_token = response.json().values()

        url = reverse('note-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(
            path=url,
            format='json'
        )
        callback_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(callback_data, [{'title': note.title, 'text': note.text}])

    def test_create_note(self):
        user = self.create_user()
        url = reverse('token_obtain_pair')
        data = {
            'email': self.email,
            'password': self.password
        }
        response = self.client.post(
            path=url,
            data=data,
            format='json'
        )
        refresh_token, access_token = response.json().values()

        url = reverse('note-list')
        data = {
            'title': self.title,
            'text': self.text
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(
            path=url,
            data=data,
            format='json'
        )
        callback_data = response.json()
        self.assertEqual(user.notes.all().count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(callback_data, {'title': self.title, 'text': self.text})

    def test_detail_note(self):
        user = self.create_user()
        note = self.create_note(user.pk)
        url = reverse('token_obtain_pair')
        data = {
            'email': self.email,
            'password': self.password
        }
        response = self.client.post(
            path=url,
            data=data,
            format='json'
        )
        refresh_token, access_token = response.json().values()

        url = reverse('note-detail', kwargs={'pk': note.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(
            path=url,
            format='json'
        )
        callback_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(callback_data, {'title': self.title, 'text': self.text})

        data = {'title': 'new title', 'text': 'new text'}
        response = self.client.put(
            path=url,
            data=data,
            format='json'
        )
        callback_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(callback_data, {'title': 'new title', 'text': 'new text'})

        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user.notes.all().count(), 0)