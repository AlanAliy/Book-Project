from django.urls import path
from .views import Register,Login, logout_class

urlpatterns = [
    path("register/", Register.as_view(), name="register" ),
    path("login/", Login.as_view(), name="login"),
    path("logout/", logout_class.as_view(), name="logout"),
]