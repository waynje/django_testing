import datetime
import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News

CREATE_MANY_COMMENTS_COUNT = 5


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )
    return comment


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
    now = timezone.now()
    for index in range(CREATE_MANY_COMMENTS_COUNT):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now - datetime.timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Текст'
    }


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def users_login_url():
    return reverse('users:login')


@pytest.fixture
def news_detail_redirect_url(users_login_url, comment):
    next_url = reverse('news:detail', args=(comment.pk,))
    return f"{users_login_url}?next={next_url}"


@pytest.fixture
def news_comment_redirect(news):
    return reverse('news:detail', args=(news.pk, )) + '#comments'


@pytest.fixture
def edit_redirect_url(users_login_url, edit_url):
    return f'{users_login_url}?next={edit_url}'


@pytest.fixture
def delete_redirect_url(users_login_url, delete_url):
    return f'{users_login_url}?next={delete_url}'
