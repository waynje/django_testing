from django.urls import reverse
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

DETAIL_URL = lazy_fixture('detail_url')


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id')),
    ),
)
def test_pages_avaliability(
    author_client, admin_client, name, args
):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    if name in ['news:delete', 'news:edit']:
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
    else:
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id'),),
        ('news:delete', pytest.lazy_fixture('comment_id')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    assertRedirects(client.get(reverse(name, args=args)),
                    f'{reverse("users:login")}?next={reverse(name,args=args)}')
