from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    all_initial_comments = list(Comment.objects.all())
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    all_comments = list(Comment.objects.all())
    assert all_initial_comments == all_comments


def test_user_can_create_comment(
        author, author_client, news, form_data):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    comment_created_count = Comment.objects.count() - initial_comments_count
    assert comment_created_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(admin_client, news_id, bad_words_data):
    all_initial_comments = list(Comment.objects.all())
    url = reverse('news:detail', args=news_id)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    all_comments = list(Comment.objects.all())
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
    initial_comments = list(Comment.objects.all())
    deleted_comment = Comment.objects.filter(pk=comment.pk)
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=news_id) + '#comments'
    assertRedirects(response, expected_url)
    assert deleted_comment not in initial_comments


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
    initial_comments = list(Comment.objects.all())
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments = list(Comment.objects.all())
    comment.refresh_from_db()
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author
    assert initial_comments == comments
