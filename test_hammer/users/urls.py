from django.urls import path

from . import views

urlpatterns = [
    path('create-code/', views.CreateCodeView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('profile/', views.ProfileView.as_view()),
]
