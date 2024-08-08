from .models import Article, Category, Comment, Content, Text, Image, Video
from .services.article_content_service import (
    get_text_preview_for_article,
    create_content,
)
from account.serializers import UserDetailUpdateSerializer
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Comment
        exclude = ["active", "article"]
        read_only_fields = ["id", "created"]


class ContentObjectRelatedField(serializers.RelatedField):
    """Поле для вывода контента разного типа (Text, Image, Video)"""

    def to_representation(self, value):
        return value.__str__()


class ContentSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)
    content_object = ContentObjectRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ["id", "content_type", "object_id", "content_object"]
        read_only_fields = ["content_type", "object_id"]


class ContentObjectBaseSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        """
        После создания объекта контента, связывает его
        со статьёй через модель Content
        """
        instance = super().create(validated_data)
        article = self.context.get("view").article
        create_content(article=article, content_object=instance)
        return instance


class TextSerializer(ContentObjectBaseSerializer):
    class Meta:
        model = Text
        fields = "__all__"


class ImageSerializer(ContentObjectBaseSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class VideoSerializer(ContentObjectBaseSerializer):
    class Meta:
        model = Video
        fields = "__all__"


class ArticleBaseSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField(source="get_article_views", read_only=True)
    users_like_count = serializers.IntegerField(
        source="users_like.count", read_only=True
    )
    rating = serializers.IntegerField(source="get_article_rating", read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)
    category = serializers.SlugRelatedField(
        slug_field="title", queryset=Category.objects.all()
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "category",
            "title",
            "preview_image",
            "published",
            "view_count",
            "users_like_count",
            "rating",
            "comment_count",
        ]
        read_only_fields = ["id", "published"]


class ArticleListSerializer(ArticleBaseSerializer):
    text_preview = serializers.SerializerMethodField("get_text_preview", read_only=True)
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta(ArticleBaseSerializer.Meta):
        fields = ArticleBaseSerializer.Meta.fields + ["text_preview", "author", "url"]

    def get_text_preview(self, article):
        return get_text_preview_for_article(article)


class ArticleDetailSerializer(ArticleBaseSerializer):
    author = UserDetailUpdateSerializer(read_only=True)
    contents = ContentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(ArticleBaseSerializer.Meta):
        fields = ArticleBaseSerializer.Meta.fields + [
            "author",
            "contents",
            "comments",
            "status",
        ]
        read_only_fields = ["status"]


class ArticleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="title", queryset=Category.objects.all()
    )
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Article
        fields = ["id", "category", "author", "title", "preview_image"]
        read_only_fields = ["id"]
