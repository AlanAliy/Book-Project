from django.db import models
from django.utils import timezone
from authors.models import Author
from users.models import User


class Book(models.Model):
    name = models.CharField(verbose_name="Name", max_length= 150)
    release_date = models.DateField(verbose_name="Release Date")
    summary = models.TextField(verbose_name="Summary", max_length=2000)
    created_at = models.DateTimeField(verbose_name="Created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated at", auto_now=True)
    authors = models.ManyToManyField(Author, related_name="books", verbose_name="Authors")

    def __str__(self) -> str:
        return f"{self.name}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Username")
    title = models.CharField(verbose_name="Title", max_length=100, null=True)
    body = models.TextField(verbose_name="Body", max_length=3000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Book")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} {self.body}"
