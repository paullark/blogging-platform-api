from .models import Article, Category, Comment, Content
from .services.article_content_service import get_text_preview_for_article
from account.serializers import UserDetailUpdateSerializer
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ArticleBaseSerializer(serializers.ModelSerializer):
    text_preview = serializers.SerializerMethodField('get_text_preview')
    view_count = serializers.IntegerField(source='get_article_views',
                                          read_only=True)
    users_like_count = serializers.IntegerField(source='users_like.count',
                                                read_only=True)
    rating = serializers.IntegerField(source='get_article_rating',
                                      read_only=True)
    comment_count = serializers.IntegerField(source='comments.count',
                                             read_only=True)
    category = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'category', 'title', 'preview_image',
            'published', 'view_count', 'users_like_count',
            'rating', 'comment_count'
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        exclude = ('active', 'article')
        read_only_fields = ('id', 'created')


class ContentObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.__str__()


class ContentSerializer(serializers.ModelSerializer):
    content_object = ContentObjectRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ('content_object',)


class ArticleListSerializer(ArticleBaseSerializer):
    text_preview = serializers.SerializerMethodField('get_text_preview')
    author = serializers.SlugRelatedField(slug_field="username",
                                          read_only=True)
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)

    class Meta(ArticleBaseSerializer.Meta):
        fields = ArticleBaseSerializer.Meta.fields + ['text_preview', 'author', 'url']

    def get_text_preview(self, article):
        return get_text_preview_for_article(article)


class ArticleDetailSerializer(ArticleBaseSerializer):
    author = UserDetailUpdateSerializer(read_only=True)
    contents = ContentSerializer(many=True)
    # comments = CommentSerializer(many=True)

    class Meta(ArticleBaseSerializer.Meta):
        fields = ArticleBaseSerializer.Meta.fields + ['author', 'contents']
