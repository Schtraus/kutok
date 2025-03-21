from . import views
from django.urls import path

app_name = 'forum'

urlpatterns = [
    path('', views.home, name='home'),
    path("threads/", views.thread_list, name='thread_list'),
    path("thread/<slug:thread_slug>/", views.thread_detail, name="thread_detail"),
    path('thread/<slug:thread_slug>/load-more-comments/', views.load_more_comments, name='load_more_comments'),
    path("category/", views.category_list, name="category_list"),
    # path("<slug:category_slug>/", views.category_page, name="category_page")
    path('thread-create/', views.ThreadCreateView.as_view(), name='thread_create'),
    path('comment/<int:comment_id>/report/', views.report_comment, name='report_comment'),


    # path('search/', views.search_threads, name='search_threads'),

]
