from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    NOTES_COUNT = 20

    @classmethod
    def setUpTestData(cls):
        all_notes = []
        cls.author = User.objects.create(username='Тестовый автор')
        for index in range(cls.NOTES_COUNT):
            notes = Note(title=f'Заметка {index}',
                         text='Просто текст',
                         author=cls.author,
                         slug=f'slug{index}')
            all_notes.append(notes)
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, self.NOTES_COUNT)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_notes_id = [note.id for note in object_list]
        sorted_notes = sorted(all_notes_id, reverse=False)
        self.assertEqual(all_notes_id, sorted_notes)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertIn('form', response.context)
