from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'slug'
URL_NOTES_HOME = reverse('notes:home')
URL_NOTES_ADD = reverse('notes:add')
URL_NOTES_EDIT = reverse('notes:edit', args=(SLUG,))
URL_NOTES_DETAIL = reverse('notes:detail', args=(SLUG,))
URL_NOTES_DELETE = reverse('notes:delete', args=(SLUG,))
URL_NOTES_LIST = reverse('notes:list')
URL_NOTES_SUCCESS = reverse('notes:success')
URL_USERS_LOGIN = reverse('users:login')
URL_USERS_LOGOUT = reverse('users:logout')
URL_USERS_SINGIN = reverse('users:signup')
URL_REDIRECT_ADD = f'{URL_USERS_LOGIN}?next={URL_NOTES_ADD}'
URL_REDIRECT_SUCCESS = f'{URL_USERS_LOGIN}?next={URL_NOTES_SUCCESS}'
URL_REDIRECT_LIST = f'{URL_USERS_LOGIN}?next={URL_NOTES_LIST}'
URL_REDIRECT_DETAIL = f'{URL_USERS_LOGIN}?next={URL_NOTES_DETAIL}'
URL_REDIRECT_EDIT = f'{URL_USERS_LOGIN}?next={URL_NOTES_EDIT}'
URL_REDIRECT_DELETE = f'{URL_USERS_LOGIN}?next={URL_NOTES_DELETE}'


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.reader = User.objects.create(username='Тестовый читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author)

    def setUp(self):
        self.client_author = Client()
        self.client_author.force_login(self.author)
        self.client_reader = Client()
        self.client_reader.force_login(self.reader)

    def test_overall_avaliability(self):
        avaliability_data = (
            (URL_NOTES_HOME, self.client_reader, HTTPStatus.OK),
            (URL_NOTES_HOME, self.client_author, HTTPStatus.OK),
            (URL_USERS_LOGIN, self.client_reader, HTTPStatus.OK),
            (URL_USERS_LOGIN, self.client_author, HTTPStatus.OK),
            (URL_USERS_SINGIN, self.client_reader, HTTPStatus.OK),
            (URL_USERS_SINGIN, self.client_author, HTTPStatus.OK),
            (URL_NOTES_EDIT, self.client_reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_EDIT, self.client_author, HTTPStatus.OK),
            (URL_NOTES_DETAIL, self.client_reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_DETAIL, self.client_author, HTTPStatus.OK),
            (URL_NOTES_DELETE, self.client_reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_DELETE, self.client_author, HTTPStatus.OK),
            (URL_USERS_LOGOUT, self.client_author, HTTPStatus.OK),
            (URL_USERS_LOGOUT, self.client_reader, HTTPStatus.OK),
        )
        for url, client, status in avaliability_data:
            with self.subTest(url=url, client=client, status=status):
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_overall_redirect(self):
        redirect_data = (
            (URL_NOTES_SUCCESS, self.client,
             URL_REDIRECT_SUCCESS),
            (URL_NOTES_ADD, self.client,
             URL_REDIRECT_ADD),
            (URL_NOTES_LIST, self.client,
             URL_REDIRECT_LIST),
            (URL_NOTES_DETAIL, self.client,
             URL_REDIRECT_DETAIL),
            (URL_NOTES_EDIT, self.client,
             URL_REDIRECT_EDIT),
            (URL_NOTES_DELETE, self.client,
             URL_REDIRECT_DELETE)
        )
        for url, user, redirect_url in redirect_data:
            with self.subTest(url=url, user=user, redirect_url=redirect_url):
                response = user.get(url)
                self.assertRedirects(response, redirect_url)
