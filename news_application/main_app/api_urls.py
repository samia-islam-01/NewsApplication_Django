from django.urls import path

from . import api_views

urlpatterns = [
    path('articles/',api_views.api_articles),
    path('articles/subscribed/',api_views.api_subscribed_articles),
    path('articles/<int:article_id>/',api_views.api_single_article),
    path('articles/create/',api_views.api_create_article),
    path('articles/<int:article_id>/update/',api_views.api_update_article),
    path('articles/<int:article_id>/delete/',api_views.api_delete_article),
    path('articles/<int:article_id>/approve/',api_views.api_approve_article),
    path('approved/', api_views.approved_article_log, name='approved_article'),
    path('newsletters/', api_views.api_newsletters),
    path('newsletters/<int:newsletter_id>/', api_views.api_single_newsletter),
    path('newsletters/create/', api_views.api_create_newsletter),
    path('newsletters/<int:newsletter_id>/update/', api_views.api_update_newsletter),
    path('newsletters/<int:newsletter_id>/delete/', api_views.api_delete_newsletter)
]