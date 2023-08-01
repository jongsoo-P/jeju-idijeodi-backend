from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.Registration.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
]