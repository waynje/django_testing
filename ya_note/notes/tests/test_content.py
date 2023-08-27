from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

SLUG = 'slug'
URL_NOTES_ADD = reverse('notes:add')
URL_NOTES_EDIT = reverse('notes:edit', args=(SLUG,))
URL_NOTES_LIST = reverse('notes:list')

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
            for index in range(NOTES_COUNT))
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author,
        )

    def test_notes_count(self):
        response = self.auth_client.get(URL_NOTES_LIST)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), NOTES_COUNT + 1)

    def test_pages_contains_form(self):
        for name in [URL_NOTES_ADD, URL_NOTES_EDIT]:
            with self.subTest(name=name):
                response = self.auth_client.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_correct_display_on_list(self):
        response = self.auth_client.get(URL_NOTES_LIST)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        note = object_list.get(pk=self.note.pk)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
