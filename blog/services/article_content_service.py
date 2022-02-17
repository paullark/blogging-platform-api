from ..models import Article, Content, Text, Image, Video
from .article_range_service import get_article_object
from .article_rating_service import ArticlesRating, ArticleViewCounter
from account.services.rating_service import UsersRating
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.utils import timezone
from typing import Union
import logging.config


USERS_RATING = UsersRating()
ARTICLES_RATING = ArticlesRating()

logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')


def get_text_preview_for_article(article: Article) -> str:
    """Функция возвращает текстовое превью статьи или пустую строку"""
    try:
        preview_content = article.contents.filter(content_type__model='text').first()
        return preview_content.content_object.text
    except AttributeError:
        LOGGER.warning(f'article {article.id}, text not found')
        return ''


def delete_article_content_by_id(content_id: int) -> None:
    """Функция удаляет контент и его содержание"""
    try:
        content = Content.objects.get(id=content_id)
        content.content_object.delete()
        content.delete()
    except Content.DoesNotExist:
        LOGGER.error(f'content {content_id} not found')
        raise Http404(f'Контент {content_id} не найден')


def get_content_object_by_model_name_and_id(
        model_name: str,
        content_object_id: int) -> Union[Text, Image, Video]:

    model = _get_model_by_name(model_name)
    if model:
        try:
            return model.objects.get(id=content_object_id)
        except model.DoesNotExist:
            LOGGER.error(f'{model_name} {content_object_id} not found')
            raise Http404(f'Контент {content_object_id} не найден')
    raise Http404(f'Контент {content_object_id} не найден: unknown model {model_name}')


def create_content(article: Article, content_object: Union[Text, Image, Video]) -> None:
    try:
        Content.objects.create(article=article, content_object=content_object)
    except Exception as e:
        LOGGER.error(f'create content error', e)


def delete_all_article_content(article_id: int) -> None:
    """Удаляет содержимое статьи и чистит её рейтинг"""
    article = get_article_object(article_id)
    for content in article.contents.all():
        content.content_object.delete()
    if article.status == 'published':
        USERS_RATING.incr_or_decr_rating_by_id(action='delete_article',
                                               object_id=article.author.id)
    ARTICLES_RATING.clear_rating_by_id(object_id=article_id)


def publish_article(article: Article) -> bool:
    """Меняет статус статьи на "опубликовано", добавляет рейтинг пользователю"""
    if article.status == 'draft':
        article.status = 'published'
        article.published = timezone.now()
        article.save()
        USERS_RATING.incr_or_decr_rating_by_id(action='create_article',
                                               object_id=article.author.id)
        return True
    return False


def change_article_views(article_id: int) -> None:
    """Увеличивает количество просмотров и рейтинг статьи на 1"""
    ArticleViewCounter().incr_view_count(article_id)
    ARTICLES_RATING.incr_or_decr_rating_by_id(action='view',
                                              object_id=article_id)


def _get_model_by_name(model_name: str) -> Union[Text, Image, Video, None]:
    """Возвращает модель одного из типов контента (Text, Image, Video)"""
    if model_name in settings.ARTICLE_CONTENT_TYPES:
        try:
            return ContentType.objects.get(app_label='blog',
                                           model=model_name).model_class()
        except ContentType.DoesNotExist:
            LOGGER.error(f'model {model_name} not found')
            return None
    LOGGER.error(f'unknown model {model_name}')
    return None