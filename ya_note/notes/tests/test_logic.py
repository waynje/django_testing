from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

SLUG = 'slug'
URL_NOTES_ADD = reverse('notes:add')
URL_NOTES_EDIT = reverse('notes:edit', args=(SLUG,))
URL_NOTES_DELETE = reverse('notes:delete', args=(SLUG,))
URL_NOTES_SUCCESS = reverse('notes:success')


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.another_author = User.objects.create(username='Другой автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.auth_another_author = Client()
        cls.auth_another_author.force_login(cls.another_author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': 'slug1'}
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author,
        )
        cls.form_data_no_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }

    def test_anonymous_user_cant_create_notes(self):
        initial_notes = set(Note.objects.all())
        self.client.post(URL_NOTES_ADD, data=self.form_data)
        notes = set(Note.objects.all())
        self.assertEqual(notes, initial_notes)

    def test_user_can_create_notes(self):
        notes_before_creation = set(Note.objects.all())
        response = self.auth_another_author.post(URL_NOTES_ADD,
                                                 data=self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        created_notes = set(Note.objects.all()) - notes_before_creation
        self.assertTrue(len(created_notes), 1)
        note = created_notes.pop()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.another_author)

    def test_not_unique_slug(self):
        initial_notes = set(Note.objects.all())
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(URL_NOTES_ADD, data=self.form_data)
        self.assertFormError(
            response, form='form',
            field='slug',
            errors=(self.note.slug) + WARNING
        )
        new_notes = set(Note.objects.all())
        self.assertEqual(new_notes, initial_notes)

    def test_empty_slug(self):
        initial_notes = set(Note.objects.all())
        response = self.auth_client.post(
            URL_NOTES_ADD,
            data=self.form_data_no_slug)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        created_notes = set(Note.objects.all()) - initial_notes
        self.assertTrue(len(created_notes), 1)
        expected_slug = slugify(self.form_data['title'])
        note = created_notes.pop()
        self.assertEqual(note.title, self.form_data_no_slug['title'])
        self.assertEqual(note.text, self.form_data_no_slug['text'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.author, self.author)


class TestEditAndDeleteNote(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок'
    EDITED_NOTE_TEXT = 'Измененный текст заметки'
    EDITED_NOTE_TITLE = 'Измененный заголовок'
    EDITED_NOTE_SLUG = 'edited_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.reader = User.objects.create(username='Тестовый пользователь')
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       slug=SLUG,
                                       author=cls.author)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.EDITED_NOTE_TITLE,
            'text': cls.EDITED_NOTE_TEXT,
            'slug': cls.EDITED_NOTE_SLUG}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(URL_NOTES_DELETE)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_reader_cant_delete_user_note(self):
        response = self.reader_client.delete(URL_NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(URL_NOTES_EDIT, data=self.form_data)
        self.assertRedirects(response, URL_NOTES_SUCCESS)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.title, self.form_data['title'])
        self.assertEqual(note_from_db.text, self.form_data['text'])
        self.assertEqual(note_from_db.slug, self.form_data['slug'])
        self.assertEqual(note_from_db.author, self.note.author)

    def test_reader_cant_edit_user_note(self):
        response = self.reader_client.post(URL_NOTES_EDIT, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)
