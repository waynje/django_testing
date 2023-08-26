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


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.reader = User.objects.create(username='Тестовый читатель')
        cls.client = Client()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author)

    def test_overall_avaliability(self):
        avaliability_data = (
            (URL_NOTES_HOME, self.reader, HTTPStatus.OK),
            (URL_NOTES_HOME, self.author, HTTPStatus.OK),
            (URL_USERS_LOGIN, self.reader, HTTPStatus.OK),
            (URL_USERS_LOGIN, self.author, HTTPStatus.OK),
            (URL_USERS_LOGOUT, self.reader, HTTPStatus.OK),
            (URL_USERS_LOGOUT, self.author, HTTPStatus.OK),
            (URL_USERS_SINGIN, self.reader, HTTPStatus.OK),
            (URL_USERS_SINGIN, self.author, HTTPStatus.OK),
            (URL_NOTES_EDIT, self.reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_EDIT, self.author, HTTPStatus.OK),
            (URL_NOTES_DETAIL, self.reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_DETAIL, self.author, HTTPStatus.OK),
            (URL_NOTES_DELETE, self.reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_DELETE, self.author, HTTPStatus.OK)
        )
        for url, user, status in avaliability_data:
            self.client.force_login(user)
            with self.subTest(url=url, user=user, status=status):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_overall_redirect(self):
        redirect_data = (
            (URL_NOTES_SUCCESS, self.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_SUCCESS}'),
            (URL_NOTES_ADD, self.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_ADD}'),
            (URL_NOTES_LIST, self.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_LIST}'),
            (URL_NOTES_DETAIL, self.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_DETAIL}'),
            (URL_NOTES_EDIT, self.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_EDIT}'),
            (URL_NOTES_DELETE, self.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_DELETE}')
        )
        for url, user, redirect_url in redirect_data:
            with self.subTest(url=url, user=user, redirect_url=redirect_url):
                response = user.get(url)
                self.assertRedirects(response, redirect_url)
