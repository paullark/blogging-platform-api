from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blog'

router = DefaultRouter()
router.register(r'articles/(?P<article_id>\d+)/comments',
                views.CommentCRUDListView,
                basename='comments')

urlpatterns = [
    path('categories/',
         views.CategoryListView.as_view(),
         name='category_list'),
    path('articles/',
         views.ArticleListView.as_view({'get': 'list'}),
         name='article_list'),
    path('articles/like-unlike/',
         views.ArticleListView.as_view({'post': 'like_unlike'}),
         name='like_or_unlike_article'),
    path('articles/<int:pk>/',
         views.ArticleListView.as_view({'get': 'retrieve'}),
         name='article_detail'),
]

urlpatterns += router.urls
