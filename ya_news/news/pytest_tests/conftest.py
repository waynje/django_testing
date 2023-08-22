import datetime
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News


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
def many_news():
    News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Текст',
             date=timezone.now() - datetime.timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def many_comments(news, author):
    comments_data = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment_data = {
            'news': news,
            'author': author,
            'text': f'Текст {index}',
            'created': timezone.now() - datetime.timedelta(days=index)
        }
        comments_data.append(comment_data)

    Comment.objects.bulk_create([Comment(**comment_data) for comment_data in
                                 comments_data])


@pytest.fixture
def form_data():
    return {
        'text': 'Текст'
    }


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', news.id)
