from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blog'

router = DefaultRouter()
router.register(r'articles',
                views.ArticleView,
                basename='article')
router.register(r'articles/(?P<article_id>\d+)/comments',
                views.CommentView,
                basename='comment')

urlpatterns = [
    path('categories/',
         views.CategoryListView.as_view(),
         name='category_list'),

    path('articles/<int:article_id>/contents/<str:content_type>/',
         views.ContentCreateUpdateDeleteView.as_view({'post': 'create'}),
         name='article_content_create'),
    path('articles/<int:article_id>/contents/<str:content_type>/<int:object_id>/',
         views.ContentCreateUpdateDeleteView.as_view({'put': 'update'}),
         name='article_content_update'),
    path('articles/<int:article_id>/contents/<int:content_id>/delete/',
         views.ContentCreateUpdateDeleteView.as_view({'delete': 'destroy'}),
         name='article_content_delete'),

    path('articles/<int:pk>/like-unlike/',
         views.LikeUnlikeView.as_view(),
         name='like_or_unlike_article'),
]

urlpatterns += router.urls
