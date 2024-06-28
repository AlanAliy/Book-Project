from django.test import TestCase, Client
from django.urls import reverse
from .models import Book, Comment
from authors.models import Author
from django.utils import timezone
from . import views
import datetime
import json
from django.utils.dateparse import parse_datetime



class TestSetupMixin:
    def create_authors(self):
        self.author1 = Author.objects.create(first_name="Nazim",
                                            last_name="Hikmet",
                                            birth_date="1947-05-25"
        )
        
        self.author2 = Author.objects.create(first_name="Tevfik",
                                             last_name="Fikret",
                                             birth_date="1943-02-12"
        )

        self.author3 = Author.objects.create(first_name="Albert",
                                            last_name="Camus",
                                            birth_date="1947-07-15"
        )
    
        
        self.author4 = Author.objects.create(first_name="George",
                                             last_name="Orwell",
                                             birth_date="1947-03-22"
        )

    def create_book(self):
        self.test_book = Book.objects.create(
            name="test name",
            release_date="2003-05-25",
            summary="this book is for a test",
        )
        self.test_book.authors.add(self.author1, self.author2)

        self.test_book2 = Book.objects.create(
        name="test name 2",
        release_date="2007-05-25",
        summary="this book is for a test 2",
        )
        self.test_book2.authors.add(self.author3)

    def create_comment(self):
        self.create_authors()
        self.create_book()
        self.test_comment = Comment.objects.create(username = "test_username",
                               title="tester_title",
                               body="tester_body",
                               book_id = self.test_book.id
        )
        
        self.test_comment2 = Comment.objects.create(username = "test_username2",
                               title="tester_title2",
                               body="tester_body2",
                               book_id = self.test_book2.id
        )


class BookTests(TestCase, TestSetupMixin):
    def setUp(self):
        self.create_authors()
        self.create_book()

    def test_book_creation(self):
        self.assertEqual(self.test_book.name, "test name")
        self.assertEqual(self.test_book.release_date, "2003-05-25")
        self.assertEqual(self.test_book.summary, "this book is for a test")
        self.assertIn(self.author1, self.test_book.authors.all())
        self.assertIn(self.author2, self.test_book.authors.all())

    def test_created_time(self):
        self.assertTrue((timezone.now() - self.test_book.created_at).total_seconds() < 1)

    
    def test_updated_at(self):
        original_updated = self.test_book.updated_at
        self.test_book.summary = "updated summary"
        self.test_book.save()
        new_updated = self.test_book.updated_at
        self.assertGreater(new_updated, original_updated)

    def test_author(self):
        self.assertEqual(str(self.author1), "Nazim Hikmet")
        self.assertEqual(str(self.author2), "Tevfik Fikret")


class CommentCreateTests(TestCase, TestSetupMixin):
    def setUp(self):
        self.client = Client()
        self.create_authors()
        self.create_book()
        self.url = reverse("create-comment", kwargs={"book_id": self.test_book.id}) #bu kısmı sor book_id buna esittir demek dogru mu

    def test_make_comment_correct(self):

        #this test makes sure that a correct comment is interpreted correctly into database
        data = { 
            "username": "test_username",
            "title": "test_title",
            "body": "test_body"    
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code,200)
        self.assertTrue(Comment.objects.filter(username= "test_username",
                                               title="test_title",
                                               body = "test_body",
                                               book = self.test_book).exists())     
        
    def test_comment_no_username(self):
        data = { 
            "username": None,
            "title": "test_title",
            "body": "test_body"    
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "username or comment body is missing")
        
    def test_username_too_short(self):
        data = { 
            "username": "aba",
            "title": "test_title",
            "body": "test_body"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()["error"], "username must be 5 or more chars")

    def test_body_is_missing(self):
        data = { 
            "username": "testertester",
            "title": "test_title",
            "body": None
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "username or comment body is missing")
        
    def test_book_does_not_exist(self):
        self.url = reverse("create-comment", kwargs = {"book_id": -1})
        data = { 
            "username": "testertester",
            "title": "test_title",
            "body": "test_body"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "book does not exist")
        
    def test_incorrect_json(self):
        response = self.client.post(self.url, "incorrect Json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "JSON decode error")

    
class RetrieveBooksTest(TestCase, TestSetupMixin):
    def setUp(self):
        self.client = Client()
        self.create_authors()
        self.create_book()
        self.url = reverse("retrieve-books", kwargs= {"book_id": self.test_book.id})

    #tests if everything works correctly for correct input
    def test_correct(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], self.test_book.name)
        self.assertEqual(data["summary"], self.test_book.summary)
        self.assertEqual(data["release_date"], str(self.test_book.release_date))
        self.assertEqual(data["authors"], [str(self.author1), str(self.author2)])

        response_created_at = parse_datetime(data["created_at"])
        response_updated_at = parse_datetime(data["updated_at"])
        
        self.assertAlmostEqual(response_created_at.timestamp(), self.test_book.created_at.timestamp(), delta=1)
        self.assertAlmostEqual(response_updated_at.timestamp(), self.test_book.updated_at.timestamp(), delta=1)

    #tests if error is given if id is wrong
    def test_incorrect_id(self):
        self.url = reverse("retrieve-books", kwargs= {"book_id": -1})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "book does not exist")
    

class EditCommentTest(TestCase, TestSetupMixin):
    def setUp(self):
        self.create_comment()
        self.client = Client()
        self.url = reverse("update-comment", kwargs={"book_id": self.test_book.id,
                                                     "comment_id": self.test_comment.id})
    
    def test_edit_comment(self):
        data = {
            "username": "test_username",
            "new_title": "new_tester_title",
            "new_body": "new_tester_body",
        }
        
        #have correct responses been given
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "comment_changed")
        self.assertEqual(response.json()["title"], "new_tester_title")
        self.assertEqual(response.json()["body"], "new_tester_body")    
        self.assertEqual(response.json()["id"], self.test_comment.id)
        self.assertIn("test_username",self.test_comment.user)

        #have values updated in database
        updated_comment = Comment.objects.get(id= self.test_comment.id)
        self.assertEqual(updated_comment.title, "new_tester_title")
        self.assertEqual(updated_comment.body, "new_tester_body")
        
    def test_no_title(self):
        data = {
            "username": "test_username",
            "new_title": None,
            "new_body": "new_tester_body",
        }
        
        #have correct responses been given
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "comment_changed")
        self.assertEqual(response.json()["title"], None)
        self.assertEqual(response.json()["body"], "new_tester_body")    
        self.assertEqual(response.json()["id"], self.test_comment.id)
        self.assertIn("test_username",self.test_comment.user)

        #have values updated in database
        updated_comment = Comment.objects.get(id= self.test_comment.id)
        self.assertEqual(updated_comment.title, None)
        self.assertEqual(updated_comment.body, "new_tester_body")

    def test_no_body(self):
        data = {
            "username": "test_username",
            "new_title": "new_tester_title",
            "new_body": None,
        }
        
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "one of required fields is missing")

    def test_no_username(self):
        data = {
            "username": None,
            "new_title": "new_tester_title",
            "new_body": "new_tester_body",
        }
         
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "one of required fields is missing")

    def test_wrong_comment_id(self):
        data = {
            "username": "test_username",
            "new_title": "new_tester_title",
            "new_body": "new_tester_body",
        }
        
        self.url = reverse("update-comment", kwargs={"book_id": self.test_book.id,
                                                     "comment_id": self.test_comment2.id})
        
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "book id and comment id do not match")
    
    def test_book_not_exist(self):
        data = {
            "username": "test_username",
            "new_title": "new_tester_title",
            "new_body": "new_tester_body",
        }
        
        self.url = reverse("update-comment", kwargs={"book_id": -1,
                                                     "comment_id":self.test_comment.id })
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "book does not exist")
    
    def test_comment_does_not_exist(self):
        data = {
            "username": "test_username",
            "new_title": "new_tester_title",
            "new_body": "new_tester_body",
        }
        
        self.url = reverse("update-comment", kwargs={"book_id": self.test_book.id,
                                                     "comment_id": -1 })
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "comment does not exist")
    
    def test_comment_is_same(self):
        data = {
            "username": "test_username",
            "new_title": "tester_title",
            "new_body": "tester_body",
        }
        
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "You have not changed anything about your comment, try again if you got something wrong")
    
    def test_incorrect_json(self):
        response = self.client.put(self.url, "incorrect Json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "JSON decode error")


class BookCommentListTest(TestCase, TestSetupMixin):
    def setUp(self):
        self.client = Client()
        self.create_comment()
        self.url = reverse("comments-list", kwargs={"book_id": self.test_book.id})

    def test_book_exists_with_comments(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Comments", data)
        self.assertEqual(len(data["Comments"]), Comment.objects.filter(book__id=self.test_book.id).count())
        self.assertEqual(data["Comments"][0]["username"], self.test_comment.user)
        self.assertEqual(data["Comments"][0]["title"], self.test_comment.title)
        self.assertEqual(data["Comments"][0]["body"], self.test_comment.body)

    def test_book_exists_without_comments(self):
        new_book = Book.objects.create(name="another test name", release_date="2003-05-25", summary="this book is for another test")
        new_book.authors.add(self.author1, self.author2)
        url = reverse("comments-list", kwargs={"book_id": new_book.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "this book does not have any comments yet")

    def test_incorrect_id(self):
        url = reverse("comments-list", kwargs={"book_id": -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error"], "book does not exist")

  
class ListBooksTest(TestCase, TestSetupMixin):
    def setUp(self):
        self.client = Client()
        self.url = reverse("list-books")
        self.create_authors()
        self.create_book()

    def test_works_proper(self):
        response = self.client.get(self.url)
        data = response.json()
        count = Book.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], count)
        self.assertEqual(len(data["book_info"]), count)
        self.assertEqual(data["book_info"][0]["id"], self.test_book.id )
        self.assertEqual(data["book_info"][0]["name"], self.test_book.name )
        self.assertIn(data["book_info"][0]["authors"], f"{self.author1}, {self.author2}" )
        self.assertEqual(data["book_info"][0]["release_date"], str(self.test_book.release_date))
