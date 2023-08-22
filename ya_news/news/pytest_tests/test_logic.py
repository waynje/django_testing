from django.urls import reverse
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == initial_comments_count


def test_user_can_create_comment(
        admin_user, admin_client, news, form_data):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=[news.pk])
    response = admin_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count > initial_comments_count
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == admin_user


def test_user_cant_use_bad_words(admin_client, news_id):
    initial_comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то text, {BAD_WORDS[0]}, еще text'}
    url = reverse('news:detail', args=news_id)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == initial_comments_count


def test_author_can_edit_comment(
        author_client, news_id, comment, form_data, news, author):
    url = reverse('news:edit', args=[comment.pk])
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=news_id) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(
        author_client, news_id, comment_id):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=news_id) + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count < initial_comments_count


def test_other_user_cant_edit_comment(
        admin_client, comment, form_data, news, author):
    url = reverse('news:edit', args=[comment.pk])
    old_comment_text = comment.text
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment_text
    assert comment.news == news
    assert comment.author == author


def test_other_user_cant_delete_comment(
        admin_client, comment_id, comment, author, news):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    comment.refresh_from_db()
    assert comment.news == news
    assert comment.author == author
    assert comments_count == initial_comments_count
