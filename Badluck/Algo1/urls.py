from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('/signup', views.signup_view, name='signup'),
    path('/login', views.login_view, name='login'),
    path('register-demo/', views.demo_register, name='demo_register'),
]