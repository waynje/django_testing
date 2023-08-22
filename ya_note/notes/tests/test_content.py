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
        all_notes = []
        cls.author = User.objects.create(username='Тестовый автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        for index in range(NOTES_COUNT):
            notes = Note(title=f'Заметка {index}',
                         text='Просто текст',
                         author=cls.author,
                         slug=f'slug{index}')
            all_notes.append(notes)
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        response = self.auth_client.get(LIST_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, NOTES_COUNT)

    def test_authorized_client_has_form(self):
        response = self.auth_client.get(ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
