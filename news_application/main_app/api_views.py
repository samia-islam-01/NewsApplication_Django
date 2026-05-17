from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Article
from .serializers import ArticleSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_articles(request):
    """Displays articles to an approved user"""
    articles = Article.objects.filter(approved=True)

    serializer = ArticleSerializer(
        articles,
        many=True
    )

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_single_article(request, article_id):
    """Displays a single article to an approved user"""
    article = get_object_or_404(
        Article,
        id=article_id,
        approved=True
    )

    serializer = ArticleSerializer(article)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_article(request):
    """Allows a journalist to create an article"""
    if request.user.role != 'journalist':
        return Response(
            {'error': 'Only journalists can create articles'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ArticleSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save(
            author=request.user,
            approved=False
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_update_article(request, article_id):
    """Allows a journalist or editor to edit an article"""
    article = get_object_or_404(Article, id=article_id)

    if request.user.role not in ['journalist', 'editor']:
        return Response(
            {'error': 'Not authorized'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.user.role == 'journalist':
        if article.author != request.user:
            return Response(
                {'error': 'You can only edit your own articles'},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = ArticleSerializer(
        article,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_article(request, article_id):
    """Allows a journalist or editor to delete an article"""
    article = get_object_or_404(Article, id=article_id)

    if request.user.role not in ['journalist', 'editor']:
        return Response(
            {'error': 'Not authorized'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.user.role == 'journalist':
        if article.author != request.user:
            return Response(
                {'error': 'Cannot delete other journalist articles'},
                status=status.HTTP_403_FORBIDDEN
            )

    article.delete()

    return Response({
        'message': 'Article deleted'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_subscribed_articles(request):
    """Displays a list of a reader's subscribed articles"""
    if request.user.role != 'reader':
        return Response(
            {'error': 'Only readers allowed'},
            status=status.HTTP_403_FORBIDDEN
        )

    publisher_articles = Article.objects.filter(
        publisher__in=request.user.subscriptions_to_publishers.all(),
        approved=True
    )

    journalist_articles = Article.objects.filter(
        author__in=request.user.subscriptions_to_journalists.all(),
        approved=True
    )

    articles = (
        publisher_articles |
        journalist_articles
    ).distinct()

    serializer = ArticleSerializer(
        articles,
        many=True
    )

    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_approve_article(request, article_id):
    """Allows an editor to approve an article"""
    if request.user.role != 'editor':
        return Response(
            {'error': 'Only editors can approve'},
            status=status.HTTP_403_FORBIDDEN
        )

    article = get_object_or_404(Article, id=article_id)

    article.approved = True
    article.save()

    return Response({
        'message': 'Article approved'
    })


@api_view(['POST'])
def approved_article_log(request):
    """Creates a log for an approved article to be used in an email to subscribed readers"""
    article_id = request.data.get('article_id')
    title = request.data.get('title')

    print(
        f"External article shared:"
        f"{article_id} - {title}"
    )

    return Response({
        'status':'logged'
    })