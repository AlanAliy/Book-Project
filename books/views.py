
from django.http import  JsonResponse
from django import forms
from django.urls import reverse
from django.conf import settings
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Book, Comment
import json


def is_missing(something, field):
    if not something:
       return True,  f"{field} is missing"
    return False, ""


class CommentForm(forms.ModelForm):
    title = forms.CharField(required=False)
    body = forms.CharField(error_messages={"required": "Body is required"}, required=True)
    username = forms.CharField(error_messages={"required": "Username is required",
                                               "min_length":"Username must be at least 5 characters",
                                               "max_length":"Username can not be more than 50 characters" },
                                                required=True, min_length=5, max_length=50)
    class Meta:
        model = Comment
        fields = ["username", 'title', 'body']


@method_decorator(csrf_exempt, name='dispatch')
class CreateComment(View):
    def get(self, request,  *args, **kwargs):
        book_id = kwargs.get("book_id")
        book = get_object_or_404(Book, id=book_id)
        form = CommentForm()
        if not request.user.is_authenticated:
            return redirect(reverse("login"))
        return render(request,"books/comment_form.html", {"form": form, "book": book})

   
    def post(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id")
        book = get_object_or_404(Book, id=book_id)

        form = CommentForm(request.POST)

        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.save()
            return redirect("comments-list", book_id=book.id)
       
        else:
            return render(request,"books/comment_form.html", {"form": form, "book": book})

    


class UpdateCommentForm(forms.Form):
        
    username = forms.CharField(max_length=30, required=False)
    new_title = forms.CharField(max_length=100, required =False)
    new_body = forms.CharField(max_length=3000, required=False)
        
    def clean_username(self):
        username = self.cleaned_data.username
        if len(username) < 5:
            raise forms.ValidationError("Username must be at least five characters")

    
    def clean_body(self):
        new_body = self.cleaned_data.new_body
        if len(new_body) < 1:
            raise forms.ValidationError("Your new body paragraph can't be left empty")
        
        
@method_decorator(csrf_exempt, name='dispatch')
class UpdateComment(View):

    def get(self, request, *args, **kwargs):
        comment_id = kwargs.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id)
        form = CommentForm()
        return render(request,"books/update_comment.html", {"form": form, "comment": comment})
    

        
    def put(self, request, *args, **kwargs):
        

        book_id = kwargs.get("book_id")
        comment_id = kwargs.get("comment_id")
        form = UpdateCommentForm(request.data)
    
        if not form.is_valid():
            return render(request, "books/update_comment.html", {"form": form, "comment": comment})            
            
        username = form.get("username")
        new_body = form.get("new_body")
        new_title = form.get("new_title")
        
        if not (Comment.objects.filter(id=comment_id).exists() or
                Book.objects.filter(id = book_id).exists()):
            return JsonResponse({"error": "book or comment id not found"}, status=404)

        comment = Comment.objects.get(id=comment_id)
        
        if int(book_id) != int(comment.book.id):
            return JsonResponse({"error": "book id and comment id do not match"}, status=400)
        
        if username !=comment.user:
            return JsonResponse({"error": "username is incorrect"}, status=404)

        comment.title = new_title
        comment.body = new_body
        comment.save()
        
        return JsonResponse({"message": "comment_changed",
                            "title": comment.title,
                            "body": comment.body,
                            "id": comment.id})
    
@method_decorator(csrf_exempt, name='dispatch')
class ListBooks(View):

    def get(self, request, *args, **kwargs):
        books = Book.objects.prefetch_related("authors").all()
        book_count = 0
        book_info = []

        for book in books:
            book_count += 1
            book_dict= {
                        "id": book.id,
                        "name": book.name,
                        "authors": ", ".join([f"{author.first_name} {author.last_name}" for author in book.authors.all()]),
                        "release_date": book.release_date
                    }
            book_info.append(book_dict)
        
        return render(request, "books/list_books.html", {"books": book_info, "book_count": book_count})
        

@method_decorator(csrf_exempt, name='dispatch')    
class RetrieveBooks(View):
    
    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id")
        books = Book.objects.prefetch_related("authors").all()
        book = books.filter(id=book_id).first()
        if not book:
            return render(request, "books/retrieve_books.html", {"error": "404 Book does not exist"})
        
        
        book_dict= {
                    "name": book.name,
                    "authors": ", ".join([f"{author.first_name} {author.last_name}" for author in book.authors.all()]),
                    "release_date": book.release_date,
                    "summary": book.summary,
                    "created_at": book.created_at,
                    "updated_at": book.updated_at
                    
        }   
        return render(request, "books/retrieve_books.html", {"book": book_dict, "book_id": book_id} )

@method_decorator(csrf_exempt, name='dispatch')  
class BookCommentList(View):
    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id")
        book = Book.objects.filter(id= book_id)
        

    
        if not book.exists():
            return render(request, "books/list_comments.html", {"error": "404 Book does not exist"})
            # return JsonResponse({"error": "book does not exist"}, status=404)
        book_name = book.first().name
        comments = Comment.objects.filter(book__id=book_id)

        if comments.count() == 0:
            return render(request, "books/list_comments.html", {"message": "this book does not have any comments"})
            # return JsonResponse({"message": "this book does not have any comments yet"})

        comments_list = [{"username": comment.user,
                                "id": comment.id,
                                "title": comment.title,
                                "body": comment.body
                                } for comment in comments]
        return render(request, "books/list_comments.html", {"comments": comments_list, "book_name": book_name})
    






    """""
    def post(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id")
        
        try:
           book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"error": "book does not exist"}, status=404)
        
        try:
            comment_info = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON decode error"}, status=400)
        
        username = comment_info.get("username")
        title = comment_info.get("title")
        body = comment_info.get("body")

        if username == None or body == None:
            return JsonResponse({"error": "username or comment body is missing"}, status=400)
        
        if len(username) < 5:
            return JsonResponse({"error": "username must be 5 or more chars"}, status=400)

        comment = Comment.objects.create(username=username, title=title, body=body, book=Book.objects.get(id=book_id))
        return JsonResponse({"message": "success",
                            "comment_id": comment.id})
    """""
    """""
    @method_decorator(csrf_exempt, name='dispatch')
class UpdateComment(View):
        
    def put(self, request, *args, **kwargs):
        
        book_id = kwargs.get("book_id")
        comment_id = kwargs.get("comment_id")
    
        try:
            comment_info = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON decode error"}, status=400)
        
        username = comment_info.get("username")
        new_body = comment_info.get("new_body")
        new_title = comment_info.get("new_title")

        if not all([username, new_body]):
            return JsonResponse({"error": "one of required fields is missing"}, status=400)
        
        #comment = Comment.objects.filter(id=comment_id).first()
        #if not comment:
        #    return JsonResponse({"error": "comment id is incorrect"}, status=404)

        if not Comment.objects.filter(id=comment_id).exists():
            return JsonResponse({"error": "comment does not exist"}, status=404)

        if not Book.objects.filter(id = book_id).exists():
            return JsonResponse({"error": "book does not exist"}, status=404)

        comment = Comment.objects.get(id=comment_id)
        
        if int(book_id) != int(comment.book.id):
            return JsonResponse({"error": "book id and comment id do not match"}, status=400)
        
        if username !=comment.username:
            return JsonResponse({"error": "username is incorrect"}, status=404)


        if comment.title == new_title and comment.body == new_body:
            return JsonResponse({"error": "You have not changed anything about your comment, try again if you got something wrong"},
                                status=400)

        comment.title = new_title
        comment.body = new_body
        comment.save()
        
        return JsonResponse({"message": "comment_changed",
                            "title": comment.title,
                            "body": comment.body,
                            "id": comment.id})
    """""