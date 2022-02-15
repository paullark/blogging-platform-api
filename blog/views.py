from .models import Article, Comment, Category
# from .services.article_content_service import \
#     get_text_preview_for_article,\
#     get_article_render_contents,\
#     get_model_by_name,\
#     get_content_object_by_model_name_and_id,\
#     create_content,\
#     delete_article_content_by_id,\
#     publish_article,\
#     delete_all_article_content
# from .services.article_like_service import like_article
from .services.article_range_service import (
    get_filtered_and_sorted_article_list,
    get_article_object,
    ArticleAuthorCategoryFilter
)
# from .services.view_mixins import PaginatorMixin, ArticleEditMixin, ArticleAttrsMixin
# from account.services.decorators import query_debugger
# from django.conf import settings
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.forms.models import modelform_factory
# from django.http import HttpRequest, HttpResponse, JsonResponse
# from django.views.generic.base import View
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.shortcuts import render, redirect
# from django.urls import reverse_lazy

from .serializers import ArticleListSerializer, CategorySerializer, ArticleDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.all()


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        filter_by = self.request.query_params.get('filter')
        order_by = self.request.query_params.get('order')
        # username = self.request.query_params.get('username')
        # category_slug = self.request.query_params.get('category')
        print(order_by)
        articles = get_filtered_and_sorted_article_list(self.request.user.username,
                                                        filter_by=filter_by, order_by=order_by)
        print(articles)
        return articles


class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self, queryset=None):
        return get_article_object(self.kwargs[self.lookup_field])
