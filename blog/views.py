from .models import Category
from .permissions import (
    IsDraftAuthor, IsPublishAuthorOrReadOnly, IsArticleContentAuthor,
    IsCommentAuthorOrReadOnly
)
from .services.article_content_service import (
    get_content_object_by_model_name_and_id,
    delete_article_content_by_id,
    publish_article,
    delete_all_article_content,
    change_article_views
)
from .services.article_like_service import like_or_unlike_article
from .services.article_range_service import (
    get_filtered_and_sorted_article_list,
    get_article_object
)
from .services.article_rating_service import ArticlesRating
from .serializers import (
    ArticleListSerializer, CategorySerializer, ArticleDetailSerializer,
    CommentSerializer, ArticleCreateSerializer,
    TextSerializer, ImageSerializer, VideoSerializer
)
from django.conf import settings
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.all()


class ArticleListCreateView(generics.ListCreateAPIView):
    permission_classes = (
        IsPublishAuthorOrReadOnly,
        IsDraftAuthor
    )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateSerializer
        return ArticleListSerializer

    def get_queryset(self):
        filter_by = self.request.query_params.get('filter')
        order_by = self.request.query_params.get('order')
        username = self.request.query_params.get('username')
        category_slug = self.request.query_params.get('category')

        articles = get_filtered_and_sorted_article_list(
            username or self.request.user.username,
            category_slug,
            filter_by, order_by
        )
        return articles

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleUpdateDeleteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = (
        IsPublishAuthorOrReadOnly,
        IsDraftAuthor
    )

    def get_object(self, queryset=None):
        article = get_article_object(self.kwargs.get('pk'))
        self.check_object_permissions(self.request, article)
        if article.status != 'draft':
            change_article_views(article.id)
        return article

    def perform_destroy(self, instance):
        delete_all_article_content(instance.id)
        instance.delete()


class CommentCRUDListView(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsCommentAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly
    )
    article = None
    rating = ArticlesRating()

    def dispatch(self, request, *args, **kwargs):
        self.article = get_article_object(kwargs.get('article_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.article.comments.all()

    def perform_create(self, serializer):
        self.rating.incr_or_decr_rating_by_id(action='add_comment',
                                              object_id=self.article.id)
        serializer.save(article=self.article, author=self.request.user)

    def perform_destroy(self, instance):
        self.rating.incr_or_decr_rating_by_id(action='delete_comment',
                                              object_id=self.article.id)
        instance.delete()


class LikeUnlikeView(APIView):
    """Поставить или убрать лайк статье"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        action = request.POST.get('action')
        if action:
            if like_or_unlike_article(request.user, pk, action):
                return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ArticlePublishView(APIView):
    permission_classes = (IsDraftAuthor,)

    def post(self, request, pk):
        if publish_article(pk):
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ContentCreateUpdateDeleteView(mixins.CreateModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):
    """Создание, изменение и удаление объектов контента статьи"""
    permission_classes = (IsArticleContentAuthor,)
    article = None
    content_type = None

    def dispatch(self, request, *args, **kwargs):
        self.article = get_article_object(kwargs.get('article_id'))
        self.content_type = self.kwargs.get('content_type')
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.content_type == 'text':
            return TextSerializer
        elif self.content_type == 'image':
            return ImageSerializer
        elif self.content_type == 'video':
            return VideoSerializer
        LOGGER.error(f'unknown content_type {self.content_type}')
        raise TypeError(f'unknown content_type {self.content_type}')

    def get_object(self):
        return get_content_object_by_model_name_and_id(model_name=self.content_type,
                                                       content_object_id=self.kwargs.get('object_id'))

    def destroy(self, request, *args, **kwargs):
        content_id = kwargs.get('content_id')
        delete_article_content_by_id(content_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
