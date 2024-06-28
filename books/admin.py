from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from  .models import Book, Comment
from authors.models import Author

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_date', 'get_authors')
    search_fields = ('name','authors__first_name', 'authors__last_name' )
    list_filter = ('created_at', 'release_date')
    readonly_fields = ('created_at', 'updated_at')
    filter_vertical = ('authors',)

    def get_fieldsets(self, request, object=None):
        if object: 
            return (
                (None, {
                    'fields': ('name', 'release_date', 'summary', 'authors'),
                    'classes': ('wide',),
                }),
                ('Additional Information', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('extrapretty', "collapse", "wide"),
                }),
            )
        return (
                (None, {
                    'fields': ('name', 'release_date', 'summary', 'authors'),
                    'classes': ('wide',),
                }),
        )




    def get_authors(self, book):
        return ", ".join([str(author) for author in book.authors.all()])

    get_authors.short_description = 'authors'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('book','title', 'user')
    fields = ('book','title', 'user', 'body')
    search_fields = ('user',)
