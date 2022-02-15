from .models import Article, Comment, Category
from .permissions import IsDraftAuthor, IsPublishOrCommentAuthor
# from .services.article_content_service import \
#     get_text_preview_for_article,\
#     get_article_render_contents,\
#     get_model_by_name,\
#     get_content_object_by_model_name_and_id,\
#     create_content,\
#     delete_article_content_by_id,\
#     publish_article,\
#     delete_all_article_content
from .services.article_like_service import like_or_unlike_article
from .services.article_range_service import (
    get_filtered_and_sorted_article_list,
    get_article_object,
)
from .services.article_rating_service import ArticleViewCounter, ArticlesRating
# from .services.view_mixins import PaginatorMixin, ArticleEditMixin, ArticleAttrsMixin

from .serializers import (
    ArticleListSerializer, CategorySerializer, ArticleDetailSerializer, CommentSerializer
)
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.all()


class ArticleListView(viewsets.ModelViewSet):
    serializer_class = ArticleListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsDraftAuthor)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_queryset(self):
        filter_by = self.request.query_params.get('filter')
        order_by = self.request.query_params.get('order')
        username = self.request.query_params.get('username')
        category_slug = self.request.query_params.get('category')
        articles = get_filtered_and_sorted_article_list(username or self.request.user.username,
                                                        category_slug,
                                                        filter_by, order_by)
        return articles

    def get_object(self, queryset=None):
        article = get_article_object(self.kwargs.get('pk'))
        self.change_article_views(article.id)
        return article

    @staticmethod
    def change_article_views(article_id: int) -> None:
        """Увеличивает количество просмотров и рейтинг статьи на 1"""
        ArticleViewCounter().incr_view_count(article_id)
        ArticlesRating().incr_or_decr_rating_by_id(action='view',
                                                   object_id=article_id)

    @action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
    def like_unlike(self, request):
        article_id = request.POST.get('article_id')
        action = request.POST.get('action')
        if article_id and action:
            if like_or_unlike_article(request.user, article_id, action):
                return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self, queryset=None):
        return get_article_object(self.kwargs[self.lookup_field])


class CommentCRUDListView(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsPublishOrCommentAuthor)
    article = None

    def dispatch(self, request, *args, **kwargs):
        self.article = get_article_object(kwargs.get('article_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.article.comments.all()

    def perform_create(self, serializer):
        serializer.save(article=self.article, author=self.request.user)
