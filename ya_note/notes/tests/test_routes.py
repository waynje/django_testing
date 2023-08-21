from http import HTTPStatus


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')
        cls.reader = User.objects.create(username='Тестовый читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author)
        cls.login_url = reverse('users:login')
        cls.list_url = reverse('notes:list')

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_add_note_for_anonymous_client(self):
        for name in ('notes:add',
                     'notes:success',
                     'notes:list'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_list_redirect_for_anonymous_client(self):
        with self.subTest():
            url = reverse('notes:list')
            redirect_url = f'{self.login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client(self):
        for name in ('notes:edit',
                     'notes:delete',
                     'notes:detail',
                     ):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_avaliability(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit',
                         'notes:detail',
                         'notes:delete',
                         ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_list_avaliability(self):
        self.client.force_login(self.author)
        with self.subTest():
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
