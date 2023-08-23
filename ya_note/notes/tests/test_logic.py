from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


User = get_user_model()

SLUG = 'slug'
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_notes(self):
        initial_notes = list(Note.objects.all())
        self.client.post(ADD_URL, data=self.form_data)
        notes = list(Note.objects.all())
        self.assertEqual(notes, initial_notes)

    def test_user_can_create_notes(self):
        initial_notes_count = Note.objects.count()
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note_count = Note.objects.count()
        self.assertLess(initial_notes_count, note_count)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_slug_must_be_unique(self):
        initial_notes_count = Note.objects.count()
        self.auth_client.post(ADD_URL, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(self.auth_client.post(ADD_URL,
                                                   data=self.form_data),
                             form='form',
                             field='slug',
                             errors=warning)
        note_count = Note.objects.count()
        self.assertEqual(note_count - initial_notes_count, 1)

    def test_empty_slug(self):
        initial_notes_count = Note.objects.count()
        del self.form_data['slug']
        response = self.auth_client.post(
            ADD_URL,
            data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count - initial_notes_count, 1)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.filter(slug=expected_slug).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.text, self.NOTE_TEXT)
        self.assertEqual(new_note.title, self.NOTE_TITLE)
        self.assertEqual(new_note.author, self.author)


class TestEditAndDeleteNote(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок'
    NOTE_SLUG = 'slug'
    EDITED_NOTE_TEXT = 'Измененный текст заметки'
    EDITED_NOTE_TITLE = 'Измененный заголовок'
    EDITED_NOTE_SLUG = 'edited_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.reader = User.objects.create(username='Тестовый пользователь')
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       slug=cls.NOTE_SLUG,
                                       author=cls.author)
        cls.url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.EDITED_NOTE_TITLE,
            'text': cls.EDITED_NOTE_TEXT,
            'slug': cls.EDITED_NOTE_SLUG}

    def test_author_can_delete_note(self):
        initial_notes = list(Note.objects.all())
        deleted_note = Note.objects.filter(pk=self.note.pk)
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertNotIn(deleted_note, initial_notes)

    def test_reader_cant_delete_user_note(self):
        initial_notes = list(Note.objects.all())
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes = list(Note.objects.all())
        self.assertEqual(initial_notes, notes)

    def test_author_can_edit_note(self):
        initial_note = Note.objects.get(pk=self.note.pk)
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, initial_note.author)

    def test_reader_cant_edit_user_note(self):
        initial_note = Note.objects.get(pk=self.note.pk)
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, initial_note)
