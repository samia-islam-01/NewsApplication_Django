from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    CustomUser,
    Article,
    Publisher,
    Newsletter
)


class APITestCase(TestCase):

    def setUp(self):

        self.client = APIClient()

        # Users
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            password="pass123",
            role="reader"
        )

        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            password="pass123",
            role="journalist"
        )

        self.journalist2 = CustomUser.objects.create_user(
            username="journalist2",
            password="pass123",
            role="journalist"
        )

        self.editor = CustomUser.objects.create_user(
            username="editor1",
            password="pass123",
            role="editor"
        )

        self.publisher = Publisher.objects.create(
            name="BBC"
        )

        # Subscriptions
        self.reader.subscriptions_to_journalists.add(
            self.journalist
        )

        self.reader.subscriptions_to_publishers.add(
            self.publisher
        )

        # Articles
        self.article1 = Article.objects.create(
            title="Subscribed article",
            content="test",
            author=self.journalist,
            approved=True
        )

        self.article2 = Article.objects.create(
            title="Not subscribed",
            content="test",
            author=self.journalist2,
            approved=True
        )

        self.publisher_article = Article.objects.create(
            title="Publisher article",
            content="test",
            publisher=self.publisher,
            author=self.journalist,
            approved=True
        )


    # Reader authentication testing (denied user)

    def test_unauthenticated_user_denied(self):

        response = self.client.get(
            "/api/articles/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    # Reader authentication testing (approved user)

    def test_authenticated_user_allowed(self):

        self.client.force_authenticate(
            user=self.reader
        )

        response = self.client.get(
            "/api/articles/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    # Reader subscription filtering

    def test_reader_only_sees_subscribed_articles(self):

        self.client.force_authenticate(
            user=self.reader
        )

        response = self.client.get(
            "/api/articles/subscribed/"
        )

        titles = [
            article["title"]
            for article in response.data
        ]

        self.assertIn(
            "Subscribed article",
            titles
        )

        self.assertIn(
            "Publisher article",
            titles
        )

        self.assertNotIn(
            "Not subscribed",
            titles
        )


    # Journalist access reader endpoint (subscriptions)

    def test_journalist_cannot_access_reader_endpoint(self):

        self.client.force_authenticate(
            user=self.journalist
        )

        response = self.client.get(
            "/api/articles/subscribed/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


    # Journalist article creation

    def test_journalist_can_create_article(self):

        self.client.force_authenticate(
            user=self.journalist
        )

        data = {
            "title":"new article",
            "content":"hello"
        }

        response = self.client.post(
            "/api/articles/create/",
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Article.objects.count(),
            4
        )


    # Reader article creation

    def test_reader_cannot_create_article(self):

        self.client.force_authenticate(
            user=self.reader
        )

        response = self.client.post(
            "/api/articles/create/",
            {
                "title":"bad",
                "content":"test"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


    # Editor article approval

    def test_editor_can_approve(self):

        article = Article.objects.create(
            title="pending",
            content="pending",
            author=self.journalist,
            approved=False
        )

        self.client.force_authenticate(
            user=self.editor
        )

        response = self.client.put(
            f"/api/articles/{article.id}/approve/"
        )

        article.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            article.approved
        )

    # Reader article approval

    def test_reader_cannot_approve(self):

        self.client.force_authenticate(
            user=self.reader
        )

        response=self.client.put(
            f"/api/articles/{self.article1.id}/approve/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )



    # Editor article deletion

    def test_editor_can_delete(self):

        self.client.force_authenticate(
            user=self.editor
        )

        response = self.client.delete(
            f"/api/articles/{self.article1.id}/delete/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            Article.objects.filter(
                id=self.article1.id
            ).exists()
        )


    # Newsletter creation

    def test_newsletter_creation(self):

        newsletter = Newsletter.objects.create(
            title="weekly",
            description="desc",
            author=self.journalist
        )

        newsletter.articles.add(
            self.article1
        )

        self.assertEqual(
            newsletter.articles.count(),
            1
        )