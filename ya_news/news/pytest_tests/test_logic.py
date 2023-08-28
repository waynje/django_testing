from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client,
                                            form_data,
                                            detail_url,
                                            news_detail_redirect_url):
    all_initial_comments = set(Comment.objects.all())
    response = client.post(detail_url, data=form_data)
    assertRedirects(response, news_detail_redirect_url)
    all_comments = set(Comment.objects.all())
    assert all_initial_comments == all_comments


def test_user_can_create_comment(
        author, author_client, news, form_data, comment,
        detail_url, news_comment_redirect):
    initial_comments = set(Comment.objects.all())
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, news_comment_redirect)
    created_comments = set(Comment.objects.all()) - initial_comments
    comment = created_comments.pop()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(admin_client, bad_words_data, detail_url):
    all_initial_comments = set(Comment.objects.all())
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    all_comments = set(Comment.objects.all())
    assert all_comments == all_initial_comments


def test_author_can_edit_comment(
        author_client, comment, form_data, edit_url, news_comment_redirect):
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, news_comment_redirect)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author


def test_author_can_delete_comment(
        author_client, comment, delete_url, news_comment_redirect):
    response = author_client.post(delete_url)
    assertRedirects(response, news_comment_redirect)
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_other_user_cant_edit_comment(
        admin_client, comment, form_data, edit_url):
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    old_comment_text = comment.text
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment_text
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author


def test_other_user_cant_delete_comment(
        admin_client, comment, delete_url):
    initial_comments = set(Comment.objects.all())
    initial_comment_author = comment.author
    initial_comment_news = comment.news
    initial_comment_text = comment.text
    response = admin_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments = set(Comment.objects.all())
    comment.refresh_from_db()
    assert comment.news == initial_comment_news
    assert comment.author == initial_comment_author
    assert comment.text == initial_comment_text
    assert initial_comments == comments
