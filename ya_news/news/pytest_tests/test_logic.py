from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    all_initial_comments = set(Comment.objects.all())
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    all_comments = set(Comment.objects.all())
    assert all_initial_comments == all_comments


def test_user_can_create_comment(
        author, author_client, news, form_data):
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    created_comment_count = Comment.objects.filter(author=author).count()
    assert created_comment_count == 1
    new_comment = Comment.objects.get(author=author)
    assert new_comment.text == form_data['text']
    assert new_comment.news == news


def test_user_cant_use_bad_words(admin_client, news_id, bad_words_data):
    all_initial_comments = set(Comment.objects.all())
    url = reverse('news:detail', args=news_id)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    all_comments = set(Comment.objects.all())
    assert all_comments == all_initial_comments


def test_author_can_edit_comment(
        author_client, news_id, comment, form_data):
    url = reverse('news:edit', args=[comment.pk])
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=news_id) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author


def test_author_can_delete_comment(
        author_client, news_id, comment_id, comment):
    initial_comments = Comment.objects.all()
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=news_id) + '#comments'
    assertRedirects(response, expected_url)
    assert (comment in initial_comments) is False


def test_other_user_cant_edit_comment(
        admin_client, comment, form_data):
    url = reverse('news:edit', args=[comment.pk])
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    old_comment_text = comment.text
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment_text
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author


def test_other_user_cant_delete_comment(
        admin_client, comment_id, comment, author, news):
    initial_comments = set(Comment.objects.all())
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    initial_comment_text = comment.text
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments = set(Comment.objects.all())
    comment.refresh_from_db()
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author
    assert comment.text == initial_comment_text
    assert initial_comments == comments
