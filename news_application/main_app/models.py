from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Publisher(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='managed_publishers',
        blank=True
    )

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='publisher_memberships',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.TextField()

    # If independent
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # If published by publisher
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=200)

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    # If independent
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # If published by publisher
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    articles = models.ManyToManyField(Article, related_name='newsletters')

    def __str__(self):
        return self.title


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']

    subscriptions_to_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name="subscribers"
    )

    subscriptions_to_journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='journalist_subscribers'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.groups.clear()

        group_map = {
            "reader": "Reader",
            "journalist": "Journalist",
            "editor": "Editor"
        }

        group_name = group_map.get(self.role)

        if group_name:
            group, created = Group.objects.get_or_create(
                name=group_name
            )

            self.groups.add(group)