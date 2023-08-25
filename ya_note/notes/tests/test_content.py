from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')

NOTES_COUNT = 10


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
            for index in range(10))
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test_slug',
            author=cls.author,
        )
        cls.urls = (
            ('notes:add', None),
            ('notes:edit', [cls.note.slug]),
        )

    def test_notes_count(self):
        response = self.auth_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), NOTES_COUNT + 1)

    def test_pages_contains_form(self):
        for name, args in self.urls:
            self.client.force_login(self.author)
            note_from_db = Note.objects.get(pk=self.note.pk)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
                self.assertEqual(self.note.title, note_from_db.title)
                self.assertEqual(self.note.text, note_from_db.text)
                self.assertEqual(self.note.slug, note_from_db.slug)
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        notes = response.context['object_list']
        note_last = notes.last()
        self.assertEqual(note_last.title, self.note.title)
        self.assertEqual(note_last.text, self.note.text)
        self.assertEqual(note_last.slug, self.note.slug)
        self.assertEqual(note_last.author, self.note.author)
