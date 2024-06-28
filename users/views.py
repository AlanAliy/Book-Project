from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django import forms
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.models import User
from users.Forms import RegisterForm, LoginForm




        
@method_decorator(csrf_exempt, name='dispatch')
class Register(View):

    def get(self,request, *args, **kwargs):
        form = RegisterForm()
        return render(request,"users/register_form.html", {"form": form})
   
    def post(self, request, *args,  **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse("list-books"))
        return render(request,"users/register_form.html", {"form": form})
    
"""
def my_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
"""
class Login(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, "users/login_form.html", {"form": form})
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password =form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect(reverse("list-books"))
            else:
                error_incorrect = "incorrect username or password"
                return render(request, "users/login_form.html", {"form": form, "error_incorrect": error_incorrect})
        
        else:

            error_invalid = "error invalid form"
            return render(request, "users/login_form.html", {"form": form, "error_incorrect": error_incorrect})
        


class logout_class(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have successfully logged out")
        #loggedoff = "success"
        #return render(request,"books/list_books.html", {"loggedoff": loggedoff})
        return redirect(reverse("list-books"))
