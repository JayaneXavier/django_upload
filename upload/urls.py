from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_form'),
    path('files/', views.upload_list, name='upload_list'),
]
