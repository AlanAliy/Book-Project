from django.urls import path
from .views import CreateComment, UpdateComment, ListBooks, RetrieveBooks, BookCommentList

urlpatterns = [
  #  path('add_book/', add_book, name='add_book'),
    path('',ListBooks.as_view(), name='list-books' ),
    path('<book_id>', RetrieveBooks.as_view(), name ='retrieve-books'),
    path('<book_id>/comments', BookCommentList.as_view(), name='comments-list'),
    path('<book_id>/create-comment/', CreateComment.as_view(), name='create-comment'),
    path('<book_id>/comment/<comment_id>/', UpdateComment.as_view(), name = 'update-comment')
] 