from django.contrib import admin
from .models import Entry, Repository


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    list_display = (
        'name', 'url'
    )


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    search_fields = ['identifier', 'repository']
    list_display = (
        'identifier', 'description', 'url', 'repository_url'
    )

    def repository_url(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % \
                (obj.repository.url, obj.repository.name)
    repository_url.short_description = 'Repository'
    repository_url.allow_tags = True
