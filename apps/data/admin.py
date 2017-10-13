from django.contrib import admin
from .models import Entry, Repository

admin.site.register(Repository)
admin.site.register(Entry)
