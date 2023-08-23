from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
NOTES_COUNT = 20


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        Note.objects.bulk_create(
            Note(title=f'Заметка {index}',
                 author=cls.author,
                 text=f'Текст {index}',
                 slug=f'slug{index}')
            for index in range(NOTES_COUNT))

    def test_notes_count(self):
        response = self.auth_client.get(LIST_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, NOTES_COUNT)

    def test_authorized_client_has_form(self):
        response = self.auth_client.get(ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
