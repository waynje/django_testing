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
        cls.avaliability_data = (
            (URL_NOTES_HOME, cls.reader, HTTPStatus.OK),
            (URL_NOTES_HOME, cls.author, HTTPStatus.OK),
            (URL_USERS_LOGIN, cls.reader, HTTPStatus.OK),
            (URL_USERS_LOGIN, cls.author, HTTPStatus.OK),
            (URL_USERS_LOGOUT, cls.reader, HTTPStatus.OK),
            (URL_USERS_LOGOUT, cls.author, HTTPStatus.OK),
            (URL_USERS_SINGIN, cls.reader, HTTPStatus.OK),
            (URL_USERS_SINGIN, cls.author, HTTPStatus.OK),
            (URL_NOTES_EDIT, cls.reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_EDIT, cls.author, HTTPStatus.OK),
            (URL_NOTES_DETAIL, cls.reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_DETAIL, cls.author, HTTPStatus.OK),
            (URL_NOTES_DELETE, cls.reader, HTTPStatus.NOT_FOUND),
            (URL_NOTES_DELETE, cls.author, HTTPStatus.OK)
        )
        cls.redirect_data = (
            (URL_NOTES_SUCCESS, cls.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_SUCCESS}'),
            (URL_NOTES_ADD, cls.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_ADD}'),
            (URL_NOTES_LIST, cls.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_LIST}'),
            (URL_NOTES_DETAIL, cls.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_DETAIL}'),
            (URL_NOTES_EDIT, cls.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_EDIT}'),
            (URL_NOTES_DELETE, cls.client,
             f'{URL_USERS_LOGIN}?next={URL_NOTES_DELETE}')
        )

    def test_overall_avaliability(self):
        for url, user, status in self.avaliability_data:
            self.client.force_login(user)
            with self.subTest(url=url, user=user, status=status):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_overall_redirect(self):
        for url, user, redirect_url in self.redirect_data:
            with self.subTest(url=url, user=user, redirect_url=redirect_url):
                response = user.get(url)
                self.assertRedirects(response, redirect_url)
