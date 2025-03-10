from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from .models import Category, Complaint, Thread, Comment, COUNTRIES
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import CreateView
from .forms import ThreadForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


def home(request):
    all_categories = Category.objects.all()
    last_threads = Thread.objects.order_by('-created_at')[:7]
    
    data = {
        'all_categories': all_categories,
        'last_threads': last_threads,
    }
    return render(request, 'forum/home.html', context=data)

# def thread_detail(request, thread_slug):
#     thread = get_object_or_404(Thread, slug=thread_slug)

#     data = {
#         'thread': thread,
#     }
#     return render(request, 'forum/thread_detail.html', context=data)


# def thread_list(request):
    country = request.GET.get('country')
    category_slug = request.GET.get('category')
    threads = Thread.objects.filter(is_active=True)

    if country:
        threads = threads.filter(country=country)
    if category_slug:
        threads = threads.filter(category__slug=category_slug)
    
    categories = Category.objects.filter(is_active=True)

    paginator = Paginator(threads, 5)  # 10 - количество элементов на странице

    # Получаем номер текущей страницы из GET-параметров
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if category_slug:
        category = Category.objects.get(slug=category_slug)
        page_title = f'{category.name}'
    else:
        page_title = "Список всіх обговорень"

    return render(request, 'forum/thread_list.html', {
        'threads': threads,
        'categories': categories,
        'countries': COUNTRIES,
        'page_title': page_title,
        'page_obj': page_obj,
    })

    # all_threads = Thread.objects.annotate(comment_count=Count('comments'))

    # data = {
    #     'all_threads': all_threads
    # }
    # return render(request, 'forum/thread_list.html', context=data)

def thread_list(request):
    country = request.GET.get('country')
    category_slug = request.GET.get('category')
    query = request.GET.get('q')  # Новый параметр для поиска
    threads = Thread.objects.filter(is_active=True)

    if query:
        threads = threads.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    if country:
        threads = threads.filter(country=country)
    if category_slug:
        threads = threads.filter(category__slug=category_slug)
    
    categories = Category.objects.filter(is_active=True)

    paginator = Paginator(threads, 5)  # 5 - количество элементов на странице

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if category_slug:
        category = Category.objects.get(slug=category_slug)
        page_title = f'{category.name}'
    else:
        page_title = "Список всіх обговорень"
    
    # Добавляем к названию страницы текст поиска, если запрос был
    if query:
        page_title = f'Результати пошуку для "{query}"'

    return render(request, 'forum/thread_list.html', {
        'threads': threads,
        'categories': categories,
        'countries': COUNTRIES,
        'page_title': page_title,
        'page_obj': page_obj,
    })

def category_list(request):
    all_categories = all_categories = Category.objects.all()

    data = {
        'all_categories': all_categories,
    }
    return render(request, 'forum/category_list.html', context=data)


def category_page(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    data = {
        'category': category,
    }
    return render(request, 'forum/category_page.html', context=data)


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = 'forum/thread_create_form.html'
    success_url = reverse_lazy('forum:thread_list')

    login_url = reverse_lazy('users:login')  # Указываем, куда перенаправлять неавторизованных пользователей
    redirect_field_name = 'next'  # Django по умолчанию передает параметр 'next' со страницей, на которую хотели попасть


    def form_valid(self, form):
        form.instance.author = self.request.user  # Привязываем автора к теме
        messages.success(self.request, 'Тема успішно створена!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, виправте помилки в формі.')
        return super().form_invalid(form)
    

def thread_detail(request, thread_slug):
    thread = get_object_or_404(Thread, slug=thread_slug)
    comments = thread.comments.all()

    latest_threads = Thread.objects.order_by('-created_at')[:7]
    popular_threads = Thread.objects.annotate(comment_count=models.Count('comments')).order_by('-comment_count')[:7]

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thread = thread
            comment.author = request.user
            comment.save()
            return redirect(thread.get_absolute_url())
    else:
        form = CommentForm()

    context = {
        'thread': thread,
        'comments': comments,
        'form': form,
        'latest_threads': latest_threads,
        'popular_threads': popular_threads,
    }
    return render(request, 'forum/thread_detail.html', context)


@require_POST
def update_comment(request, comment_id):
    try:
        data = json.loads(request.body)
        content = data.get('content')

        if not content:
            return JsonResponse({'success': False, 'error': 'Контент комментария не может быть пустым'})

        comment = Comment.objects.get(id=comment_id)
        if comment.author == request.user:
            comment.content = content
            comment.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Нет прав для редактирования'})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Комментарий не найден'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Ошибка парсинга JSON'})

# def search_threads(request):


    query = request.GET.get('q')
    results = Thread.objects.filter(is_active=True)

    if query:
        results = results.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    categories = Category.objects.filter(is_active=True)

    paginator = Paginator(results, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'forum/thread_list.html', {
        'threads': results,
        'categories': categories,
        'countries': COUNTRIES,
        'page_title': f'Результати пошуку для "{query}"',
        'page_obj': page_obj,
    })

@login_required
def report_comment(request, comment_id):
    if request.method == 'POST':
        try:
            print("Request Body:", request.body.decode('utf-8'))
            # Парсим JSON из body запроса
            data = json.loads(request.body)
            reason = data.get('reason')  # Извлекаем значение причины

            # Получаем комментарий
            comment = Comment.objects.get(id=comment_id)

            # Создаем жалобу
            Complaint.objects.create(comment=comment, user=request.user, reason=reason)

            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Комментарий не найден'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Ошибка при разборе данных'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Неверный запрос'})


@login_required
def delete_comment(request, comment_id):
    if request.method == 'POST':
        try:
            comment = Comment.objects.get(id=comment_id, author=request.user)  # Проверяем, что комментарий принадлежит текущему пользователю
            comment.delete()
            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Комментарий не найден или не принадлежит вам'})
    return JsonResponse({'success': False, 'error': 'Неверный запрос'})