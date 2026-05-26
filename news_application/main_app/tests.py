from django.test import TestCase
from django.core import mail
from unittest.mock import patch

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
        """Set up different users, subscriptions, articles and newsletters"""
        self.client = APIClient()

        # Users
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            password="pass123",
            email="reader@test.com",
            role="reader"
        )

        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            password="pass123",
            email="journalist@test.com",
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


    def test_unauthenticated_user_denied(self):
        """Reader authentication testing"""
        response = self.client.get(
            "/api/articles/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    def test_authenticated_user_allowed(self):
        """Reader authentication testing"""
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


    def test_reader_only_sees_subscribed_articles(self):
        """Reader subscription filtering"""
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


    def test_journalist_cannot_access_reader_endpoint(self):
        """Journalist denied reader endpoint"""
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


    def test_journalist_can_create_article(self):
        """Journalist article creation"""
        self.client.force_authenticate(
            user=self.journalist
        )

        response = self.client.post(
            "/api/articles/create/",
            {
                "title":"new article",
                "content":"hello"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Article.objects.count(),
            4
        )


    def test_reader_cannot_create_article(self):
        """Reader article creation denied"""
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


    def test_invalid_article_returns_404(self):
        """Invalid article id"""
        self.client.force_authenticate(
            user=self.reader
        )

        response = self.client.get(
            "/api/articles/99999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )


    def test_journalist_invalid_put(self):
        """Invalid PUT request"""
        self.client.force_authenticate(
            user=self.journalist
        )

        response = self.client.put(
            f"/api/articles/{self.article1.id}/update/",
            {
                "title":"",
                "content":"updated"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    @patch("main_app.api_views.requests.post")
    def test_editor_can_approve(self, mock_post):
        """Editor article approval"""
        article = Article.objects.create(
            title="pending",
            content="pending",
            author=self.journalist,
            approved=False
        )

        self.client.force_authenticate(user=self.editor)

        response = self.client.put(
            f"/api/articles/{article.id}/approve/"
        )

        article.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(article.approved)

        # Verify API trigger happened
        mock_post.assert_called_once()


    def test_reader_cannot_approve(self):
        """Reader article approval"""
        self.client.force_authenticate(
            user=self.reader
        )

        response = self.client.put(
            f"/api/articles/{self.article1.id}/approve/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


    def test_editor_can_delete(self):
        """Editor deletion of articles"""
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


    def test_reader_can_view_newsletters(self):
        """Reader able to view newsletters"""
        self.client.force_authenticate(
            user=self.reader
        )

        response=self.client.get(
            "/newsletters/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_reader_cannot_edit_newsletter_api(self):
        """Reader able to edit newsletters"""
        newsletter = Newsletter.objects.create(
            title="weekly",
            description="test",
            author=self.journalist
        )

        self.client.force_authenticate(user=self.reader)

        response = self.client.put(
            f"/api/newsletters/{newsletter.id}/update/",
            {
                "title": "hacked",
                "description": "bad"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_journalist_can_create_newsletter_api(self):
        """Journalists able to create newsletters"""
        self.client.force_authenticate(user=self.journalist)

        response = self.client.post(
            "/api/newsletters/create/",
            {
                "title": "weekly",
                "description": "test",
                "articles": [self.article1.id]
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_reader_cannot_create_newsletter_api(self):
        """Journalist able to create newsletters"""
        self.client.force_authenticate(user=self.reader)

        response = self.client.post(
            "/api/newsletters/create/",
            {
                "title": "hack",
                "description": "test"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_invalid_newsletter_returns_404(self):
        """Invalid newsletter id returns 404"""
        self.client.force_authenticate(user=self.reader)

        response = self.client.get("/api/newsletters/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_reader_cannot_delete_newsletter_api(self):
        """Reader able to delete newsletters"""
        newsletter = Newsletter.objects.create(
            title="weekly",
            description="test",
            author=self.journalist
        )

        self.client.force_authenticate(user=self.reader)

        response = self.client.delete(
            f"/api/newsletters/{newsletter.id}/delete/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_newsletters_api(self):
        """Get all newsletters"""
        self.client.force_authenticate(user=self.reader)

        response = self.client.get("/api/newsletters/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)