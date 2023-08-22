import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')
DETAIL_URL = pytest.lazy_fixture('detail_url')


@pytest.mark.usefixtures('many_news')
def test_news_count(client):
    assert len(client.get(HOME_URL).
               context['object_list']) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client):
    all_dates = [news.date for news in client.get(HOME_URL).
                 context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.parametrize(
    'user, has_access', ((pytest.lazy_fixture('admin_client'), True),
                         (pytest.lazy_fixture('client'), False))
)
def test_comment_form_availability_for_different_users(
        news_id, user, has_access):
    url = reverse('news:detail', args=news_id)
    context = user.get(url).context
    if has_access:
        assert 'form' in context
        assert isinstance(context['form'], CommentForm)


@pytest.mark.usefixtures('many_comments')
def test_comments_order(client, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created < all_comments[i + 1].created
