from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [
    path('my-articles/', views.my_articles, name='my_articles'),
    path('create-article/', views.create_article, name='create_article'),
    path('edit-article/<int:article_id>/', views.edit_article, name='edit_article'),
    path('delete-article/<int:article_id>/', views.delete_article, name='delete_article'),
    path('articles/', views.article_catalogue, name='article_catalogue'),
    path('article/<int:article_id>/', views.view_article, name='view_article'),

    path('my-newsletters/', views.my_newsletters, name='my_newsletters'),
    path('create-newsletter/', views.create_newsletter, name='create_newsletter'),
    path('edit-newsletter/<int:newsletter_id>/', views.edit_newsletter, name='edit_newsletter'),
    path('delete-newsletter/<int:newsletter_id>/', views.delete_newsletter, name='delete_newsletter'),
    path('newsletters/', views.newsletter_catalogue, name='newsletter_catalogue'),
    path('newsletter/<int:newsletter_id>/', views.view_newsletter, name='view_newsletter'),

    path('manage-articles/', views.manage_articles, name='manage_articles'),
    path('approve-article/<int:article_id>/', views.approve_article, name='approve_article'),

    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/<int:publisher_id>/subscribe/', views.subscribe_publisher, name='subscribe_publisher'),
    path('publishers/<int:publisher_id>/unsubscribe/', views.unsubscribe_publisher, name='unsubscribe_publisher'),
    path('create-publisher/', views.create_publisher, name='create_publisher'),

    path('journalists/', views.journalist_list, name='journalist_list'),
    path('journalists/<int:journalist_id>/subscribe/', views.subscribe_journalist, name='subscribe_journalist'),
    path('journalists/<int:journalist_id>/unsubscribe/', views.unsubscribe_journalist, name='unsubscribe_journalist'),

    path('subscriptions/', views.my_subscriptions, name='my_subscriptions'),
]