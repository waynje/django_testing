from django.urls import reverse
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
HOME_URL = reverse('news:home')
DETAIL_URL = lazy_fixture('detail_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
LOGIN_URL = reverse('users:login')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
EDIT_REDIRECT_URL = f'{LOGIN_URL}?next={EDIT_URL}'
DELETE_REDIRECT_URL = f'{LOGIN_URL}?next={[(DELETE_URL)]}'


@pytest.mark.parametrize(
    'url, user, status',
    (
        (HOME_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (HOME_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, ADMIN_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK)
    )
)
def test_overall_avaliability(
    url, user, status
):
    response = user.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url, redirect_url',
    (
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('edit_redirect_url'),),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('delete_redirect_url'),),
    ),
)
def test_redirects_for_anonymous_client(client, url, redirect_url):
    assertRedirects(client.get(url), redirect_url)
