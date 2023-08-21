import pytest
from django.urls import reverse
from django.conf import settings

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('bulk_create_news')
def test_news_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('bulk_create_news')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'user, has_access', ((pytest.lazy_fixture('admin_client'), True),
                         (pytest.lazy_fixture('client'), False))
)
def test_comment_form_availability_for_different_users(
        news_id, user, has_access):
    url = reverse('news:detail', args=news_id)
    response = user.get(url)
    result = 'form' in response.context
    assert result == has_access


@pytest.mark.usefixtures('bulk_create_comments')
def test_comments_order(client, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created
