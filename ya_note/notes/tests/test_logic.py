from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


User = get_user_model()

ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': 'slug'}
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug1',
            author=cls.author,
        )
        cls.form_data_no_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }

    def test_anonymous_user_cant_create_notes(self):
        initial_notes = list(Note.objects.all())
        self.client.post(ADD_URL, data=self.form_data)
        notes = list(Note.objects.all())
        self.assertEqual(sorted(notes), sorted(initial_notes))

    def test_user_can_create_notes(self):
        initial_notes_count = Note.objects.count()
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note_count = Note.objects.count()
        self.assertEqual(note_count - initial_notes_count, 1)
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.title, self.form_data['title'])

    def test_not_unique_slug(self):
        initial_note_count = Note.objects.count()
        self.client.force_login(self.author)
        self.form_data['slug'] = self.notes.slug
        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertFormError(
            response, form='form',
            field='slug',
            errors=(self.notes.slug) + WARNING
        )
        new_note_count = Note.objects.count()
        self.assertEqual(new_note_count, initial_note_count)
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.author, self.author)
        self.assertEqual(self.notes.title, self.form_data['title'])

    def test_empty_slug(self):
        initial_notes_count = Note.objects.count()
        del self.form_data['slug']
        response = self.auth_client.post(
            ADD_URL,
            data=self.form_data_no_slug)
        self.assertRedirects(response, SUCCESS_URL)
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count - initial_notes_count, 1)
        expected_slug = slugify(self.form_data['title'])
        self.form_data_no_slug['slug'] = expected_slug
        new_note = Note.objects.get(slug=self.form_data_no_slug['slug'])
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.text, self.form_data_no_slug['text'])
        self.assertEqual(new_note.title, self.form_data_no_slug['title'])
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(self.form_data_no_slug['slug'], expected_slug)


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
        initial_notes = Note.objects.all()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertNotIn(self.note, initial_notes)

    def test_reader_cant_delete_user_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes = Note.objects.all()
        self.assertIn(self.note, notes)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.title, self.form_data['title'])
        self.assertEqual(note_from_db.text, self.form_data['text'])
        self.assertEqual(note_from_db.slug, self.form_data['slug'])
        self.assertEqual(note_from_db.author, self.author)

    def test_reader_cant_edit_user_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)
