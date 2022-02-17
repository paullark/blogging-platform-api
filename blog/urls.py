from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blog'

router = DefaultRouter()
router.register(r'articles/(?P<article_id>\d+)/comments',
                views.CommentCRUDListView,
                basename='comments')
# router.register(r'articles/(?P<article_id>\d+)/contents',
#                 views.ContentView,
#                 basename='content')

urlpatterns = [
    path('categories/',
         views.CategoryListView.as_view(),
         name='category_list'),
    path('articles/',
         views.ArticleListCreateView.as_view(),
         name='article_list_create'),
    path('articles/<int:pk>/like-unlike/',
         views.LikeUnlikeView.as_view(),
         name='like_or_unlike_article'),
    path('articles/<int:pk>/',
         views.ArticleUpdateDeleteDetailView.as_view(),
         name='article_detail_update_delete'),
    path('articles/<int:pk>/publish/',
         views.ArticlePublishView.as_view(),
         name='article_publish'),
    # path('articles/<int:article_id>/contents/',
    #      views.ContentCreateUpdateListView.as_view({'get': 'list'}),
    #      name='article_content_list'),
    path('articles/<int:article_id>/contents/<str:content_type>/create/',
         views.ContentCreateUpdateDeleteView.as_view({'post': 'create'}),
         name='article_content_create'),
    # path('articles/<int:article_id>/contents/<str:content_type>/<int:object_id>/',
    #      views.ContentCreateUpdateListView.as_view({'get': 'retrieve'})),
    path('articles/<int:article_id>/contents/<str:content_type>/<int:object_id>/update/',
         views.ContentCreateUpdateDeleteView.as_view({'put': 'update'}),
         name='article_content_update'),
    path('articles/<int:article_id>/contents/<int:content_id>/delete/',
         views.ContentCreateUpdateDeleteView.as_view({'delete': 'destroy'}),
         name='article_content_delete'),
]

urlpatterns += router.urls
