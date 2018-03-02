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
    search_fields = ['identifier', ]
    list_display = (
        'identifier', 'description', 'url'
    )
    list_filter = ('repository', )
