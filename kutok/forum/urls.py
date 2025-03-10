from . import views
from django.urls import path

app_name = 'forum'

urlpatterns = [
    path('', views.home, name='home'),
    path("threads/", views.thread_list, name='thread_list'),
    path("thread/<slug:thread_slug>/", views.thread_detail, name="thread_detail"),
    path("category/", views.category_list, name="category_list"),
    # path("<slug:category_slug>/", views.category_page, name="category_page")
    path('thread-create/', views.ThreadCreateView.as_view(), name='thread_create'),
    path('comments/update/<int:comment_id>/', views.update_comment, name='update_comment'),
    path('comments/report/<int:comment_id>/', views.report_comment, name='report_comment'),
    path('comments/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),


    # path('search/', views.search_threads, name='search_threads'),

]
