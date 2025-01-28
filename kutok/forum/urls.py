from . import views
from django.urls import path

app_name = 'forum'

urlpatterns = [
    path('', views.home, name='home'),
    path("threads/", views.thread_list, name="thread_list"),
    path("thread/<slug:thread_slug>/", views.thread_detail, name="thread_detail"),
    path("category/", views.category_list, name="category_list")
]
