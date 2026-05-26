import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Article, Newsletter, Publisher, CustomUser

# User Groups
def is_journalist(user):
    return (
        user.role == "journalist"
        or user.groups.filter(name="Journalist").exists()
    )


def is_editor(user):
    return (
        user.role == "editor"
        or user.groups.filter(name="Editor").exists()
    )


def is_reader(user):
    return (
        user.role == "reader"
        or user.groups.filter(name="Reader").exists()
    )


# ARTICLES
@login_required
def create_article(request):
    """Allows a journalist to create an article"""
    if not is_journalist(request.user):
        return HttpResponse("Only Journalists can create articles")

    # Publishers this journalist belongs to
    user_publishers = Publisher.objects.filter(
        journalists=request.user
    )

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')

        publish_mode = request.POST.get('publish_mode')

        publisher = None

        # If publishing under publisher
        if publish_mode == 'publisher':

            publisher_id = request.POST.get('publisher')

            publisher = get_object_or_404(
                Publisher,
                id=publisher_id,
                journalists=request.user
            )

        Article.objects.create(
            title=title,
            author=request.user,
            publisher=publisher,
            content=content,
            approved=False
        )

        return redirect('main_app:my_articles')

    return render(request, 'main_app/create_article.html', {
        'publishers': user_publishers
    })


@login_required
def my_articles(request):
    """Allows a journalist to view their own articles"""
    if not is_journalist(request.user):
        return HttpResponse("Only Journalists can view their own articles")

    # Only show articles owned by this user
    author_articles = Article.objects.filter(author=request.user)

    return render(request, 'main_app/my_articles.html', {
        'articles': author_articles
    })


@login_required
def edit_article(request, article_id):
    """Allows journalists and editors to edit articles"""
    article = get_object_or_404(Article, id=article_id)

    # Permissions
    if is_journalist(request.user):
        if article.author != request.user:
            return HttpResponse("You can only edit your own articles")

    elif not is_editor(request.user) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    if request.method == 'POST':
        article.title = request.POST['title']
        article.content = request.POST['content']

        # Editors can approve
        if is_editor(request.user):
            article.approved = request.POST.get('approved') == 'on'

        article.save()
        return redirect('main_app:manage_articles' if is_editor(request.user) else 'main_app:my_articles')

    return render(request, 'main_app/edit_article.html', {'article': article})


@login_required
def delete_article(request, article_id):
    """Allows journalists and editors to delete articles"""
    article = get_object_or_404(Article, id=article_id)

    if is_journalist(request.user):
        if article.author != request.user:
            return HttpResponse("You can only delete your own articles")

    elif not is_editor(request.user) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    article.delete()
    return redirect('main_app:manage_articles' if is_editor(request.user) else 'main_app:my_articles')


def article_catalogue(request):
    """Displays all articles"""
    query = request.GET.get('q')

    articles = Article.objects.filter(approved=True)

    if query:
        articles = articles.filter(title__icontains=query)

    return render(request, 'main_app/article_catalogue.html', {
        'articles': articles
    })


@login_required
def manage_articles(request):
    """Allows editors to manage articles"""
    if not is_editor(request.user) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    articles = Article.objects.all().order_by('-created_at')

    return render(request, 'main_app/manage_articles.html', {
        'articles': articles
    })


@login_required
def approve_article(request, article_id):
    """Allows editors to approve an article"""
    if not is_editor(request.user) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if article.approved:
        article.approved = False
        article.save()
        return redirect('main_app:manage_articles')

    article.approved = True
    article.save()

    subscribers = CustomUser.objects.none()

    # Subscribers to publisher
    if article.publisher:

        publisher_subscribers = article.publisher.subscribers.all()

        subscribers = subscribers | publisher_subscribers

    # Subscribers to journalist
    journalist_subscribers = article.author.journalist_subscribers.all()

    subscribers = (subscribers | journalist_subscribers).distinct()

    for user in subscribers:

        if user.email:

            send_mail(
                subject=f"New article: {article.title}",

                message=
                f"""
Hello {user.username}

A new article from someone you subscribe to has been published.

Title:
{article.title}

Author:
{article.publisher.name if article.publisher else article.author.username}

Content:
{article.content}
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True
            )

    try:

        requests.post(
            "http://127.0.0.1:8000/api/approved/",
            json={
                "article_id": article.id,
                "title": article.title,
                "publisher":
                article.publisher.name if article.publisher else None
            }
        )

    except Exception:
        pass


    return redirect('main_app:manage_articles')


def view_article(request, article_id):
    """ALlows users to view a specific article"""
    article = get_object_or_404(
        Article,
        id=article_id,
        approved=True
    )

    return render(request, 'main_app/view_article.html', {
        'article': article
    })


# NEWSLETTERS
@login_required
def create_newsletter(request):
    """Allows journalists to create a newsletter"""
    if not is_journalist(request.user) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    # Get articles this user can choose from
    user_articles = Article.objects.filter(author=request.user, approved=True)

    # Publishers this journalist belongs to
    user_publishers = Publisher.objects.filter(
        journalists=request.user
    )

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        selected_articles = request.POST.getlist('articles')

        publish_mode = request.POST.get('publish_mode')
        publisher = None

        if publish_mode == 'publisher':
            publisher_id = request.POST.get('publisher')

            publisher = get_object_or_404(
                Publisher,
                id=publisher_id,
                journalists=request.user
            )

        if not selected_articles:
            return render(request, 'main_app/create_newsletter.html', {
                'articles': user_articles,
                'error': 'You must select at least one article'
            })

        newsletter = Newsletter.objects.create(
            title=title,
            description=description,
            author=request.user,
            publisher=publisher,
        )

        # Add selected articles
        newsletter.articles.set(selected_articles)

        return redirect('main_app:newsletter_catalogue')

    return render(request, 'main_app/create_newsletter.html', {
        'articles': user_articles, 'publishers': user_publishers
    })


@login_required
def edit_newsletter(request, newsletter_id):
    """Allows journalists and editors to edit a newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    # Permissions
    if not (is_journalist(request.user) or is_editor(request.user)) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    # Articles available to select
    if is_editor(request.user):
        articles = Article.objects.all()
    else:
        # Journalists can only select articles belonging to them
        articles = Article.objects.filter(author=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        selected_articles = request.POST.getlist('articles')

        if not selected_articles:
            return render(request, 'main_app/edit_newsletter.html', {
                'newsletter': newsletter,
                'articles': articles,
                'error': 'You must select at least one article'
            })

        newsletter.title = title
        newsletter.description = description
        newsletter.save()

        newsletter.articles.set(selected_articles)

        return redirect('main_app:newsletter_catalogue')

    return render(request, 'main_app/edit_newsletter.html', {
        'newsletter': newsletter,
        'articles': articles
    })


@login_required
def delete_newsletter(request, newsletter_id):
    """Allows journalists and editors to delete a newsletter"""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if not (is_journalist(request.user) or is_editor(request.user)) or not request.user.is_authenticated:
        return HttpResponse("Not authorised", status=403)

    if request.method == 'POST':
        newsletter.delete()
        return redirect('main_app:newsletter_catalogue')

    return render(request, 'main_app/delete_newsletter.html', {
        'newsletter': newsletter
    })


def newsletter_catalogue(request):
    query = request.GET.get('q')

    newsletters = Newsletter.objects.all()

    if query:
        newsletters = newsletters.filter(title__icontains=query)

    return render(request, 'main_app/newsletter_catalogue.html', {
        'newsletters': newsletters
    })


@login_required
def my_newsletters(request):
    """Allows a journalist to view their own newsletters"""
    if not is_journalist(request.user) or not request.user.is_authenticated:
        return HttpResponse("Only Journalists can view their own newsletters")

    # Only show newsletters owned by this user
    author_newsletter = Newsletter.objects.filter(author=request.user)

    return render(request, 'main_app/my_newsletters.html', {
        'newsletters': author_newsletter
    })


def view_newsletter(request, newsletter_id):
    """Allows a user to view a newsletter"""
    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id
    )

    return render(request, 'main_app/view_newsletter.html', {
        'newsletter': newsletter
    })


# READER SUBSCRIPTIONS
@login_required
def my_subscriptions(request):
    """Displays a list of a reader's subscriptions to them"""
    if not is_reader(request.user):
        return HttpResponse("Only readers can view subscriptions")

    journalists = request.user.subscriptions_to_journalists.all()

    publishers = request.user.subscriptions_to_publishers.all()

    publisher_articles = Article.objects.filter(
        publisher__in=request.user.subscriptions_to_publishers.all(),
        approved=True
    )

    journalist_articles = Article.objects.filter(
        author__in=request.user.subscriptions_to_journalists.all(),
        approved=True
    )

    articles = (publisher_articles | journalist_articles).distinct()

    return render(request, 'main_app/my_subscriptions.html', {
        'journalists': journalists,
        'publishers': publishers,
        'articles' : articles
    })


# PUBLISHER
@login_required
def create_publisher(request):
    """Allows an editor to create a publisher"""
    if not is_editor(request.user) or not request.user.is_authenticated:
        return HttpResponse("Only editors can create publishers")

    journalists = CustomUser.objects.filter(
        role='journalist'
    ) | CustomUser.objects.filter(
        groups__name='Journalist'
    )
    editors = CustomUser.objects.filter(role='editor')

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')

        selected_journalists = request.POST.getlist('journalists')
        selected_editors = request.POST.getlist('editors')

        publisher = Publisher.objects.create(
            name=name,
            description=description
        )

        publisher.journalists.set(selected_journalists)
        publisher.editors.set(selected_editors)

        return redirect('main_app:publisher_list')

    return render(request, 'main_app/create_publisher.html', {
        'journalists': journalists,
        'editors': editors
    })


def publisher_list(request):
    """Displays a list of all publishers"""
    publishers = Publisher.objects.all()

    return render(request, 'main_app/publisher_list.html', {
        'publishers': publishers
    })

@login_required
def subscribe_publisher(request, publisher_id):
    """Allows a reader to subscribe to a publisher"""
    if not is_reader(request.user):
        return HttpResponse("Only readers can subscribe")

    publisher = get_object_or_404(Publisher, id=publisher_id)

    request.user.subscriptions_to_publishers.add(publisher)

    return redirect('main_app:publisher_list')


@login_required
def unsubscribe_publisher(request, publisher_id):
    """Allows a reader to unsubscribe to a publisher"""
    if not is_reader(request.user):
        return HttpResponse("Only readers can unsubscribe")

    publisher = get_object_or_404(Publisher, id=publisher_id)

    request.user.subscriptions_to_publishers.remove(publisher)

    return redirect('main_app:publisher_list')


# JOURNALIST
def journalist_list(request):
    """Displays a list of all journalists"""
    journalists = CustomUser.objects.filter(
        role='journalist'
    ) | CustomUser.objects.filter(
        groups__name='Journalist'
    )

    return render(request, 'main_app/journalist_list.html', {
        'journalists': journalists
    })


@login_required
def subscribe_journalist(request, journalist_id):
    """Allows a reader to subscribe to a journalist"""
    if not is_reader(request.user):
        return HttpResponse("Only readers can subscribe")

    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role='journalist'
    )

    request.user.subscriptions_to_journalists.add(journalist)

    return redirect('main_app:journalist_list')


@login_required
def unsubscribe_journalist(request, journalist_id):
    """Allows a reader to unsubscribe to a journalist"""
    if not is_reader(request.user):
        return HttpResponse("Only readers can unsubscribe")

    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role='journalist'
    )

    request.user.subscriptions_to_journalists.remove(journalist)

    return redirect('main_app:journalist_list')
