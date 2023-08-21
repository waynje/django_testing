import datetime
import pytest

from django.conf import settings
from django.utils import timezone
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return comment.id,


@pytest.fixture
def bulk_create_news():
    News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Текст',
             date=timezone.now()-datetime.timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def bulk_create_comments(news, author):
    for index in range(11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=timezone.now()-datetime.timedelta(days=index)
        )
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Текст'
    }
