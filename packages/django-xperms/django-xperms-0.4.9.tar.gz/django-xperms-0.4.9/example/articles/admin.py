from django.contrib import admin
from xperms.admin import PermModelAdmin

from articles.models import Article


@admin.register(Article)
class ArticleAdmin(PermModelAdmin):

    perms_per_instance = True
