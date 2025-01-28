from django.shortcuts import get_object_or_404, render

from .models import Category, Thread
from django.db.models import Count

# Create your views here.
def home(request):
    all_categories = Category.objects.all()
    last_threads = Thread.objects.order_by('-created_at')[:7]
    
    data = {
        'all_categories': all_categories,
        'last_threads': last_threads,
    }
    return render(request, 'forum/home.html', context=data)

def thread_detail(request, thread_slug):
    thread = get_object_or_404(Thread, slug=thread_slug)

    data = {
        'thread': thread,
    }
    return render(request, 'forum/thread_detail.html', context=data)

def thread_list(request):
    # all_threads = Thread.objects.all()
    all_threads = Thread.objects.annotate(comment_count=Count('comments'))

    data = {
        'all_threads': all_threads
    }
    return render(request, 'forum/thread_list.html', context=data)

def category_list(request):
    all_categories = all_categories = Category.objects.all()

    data = {
        'all_categories': all_categories,
    }
    return render(request, 'forum/category_list.html', context=data)