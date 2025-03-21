from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from .models import Category, Complaint, Thread, Comment, Country
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
from django.template.loader import render_to_string
from datetime import datetime, timezone



def home(request):
    # Получаем все категории с подкатегориями, тредами и комментариями
    all_categories = Category.objects.all().prefetch_related(
        # Для каждой категории подкатегории
        'subcategories',
        # Для каждой подкатегории треды
        'subcategories__threads',
        # Для каждого треда комментарии
        'subcategories__threads__comments'
    )

    # Подсчитываем количество тредов и комментариев для каждой подкатегории
    for category in all_categories:
        for subcategory in category.subcategories.all():
            # Количество тредов в подкатегории
            subcategory.threads_count = subcategory.threads.count()
            # Количество комментариев для всех тредов подкатегории
            subcategory.comments_count = subcategory.threads.aggregate(
                total_comments=Count('comments')
            )['total_comments']
    
    # Получаем последние обсуждения
    last_threads = Thread.objects.order_by('-created_at')[:7]
    
    data = {
        'all_categories': all_categories,
        'last_threads': last_threads,
    }
    
    return render(request, 'forum/home.html', context=data)


def thread_list(request):
    country_code = request.GET.get('country')  # Код страны
    category_slug = request.GET.get('category')  # Слаг категории
    search_query = request.GET.get('q', '') # Поисковой запрос

    # Начальная выборка всех активных тредов, сортировка от новых к старым
    threads = Thread.objects.filter(is_active=True).order_by('-created_at')

    # Фильтрация по поисковому запросу (по заголовку и контенту)
    if search_query:
        threads = threads.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # Получаем все страны для фильтра
    countries = Country.objects.all()

    # Фильтрация по стране (если передан код страны)
    country_obj = None
    if country_code:
        try:
            country_obj = Country.objects.get(code=country_code)
            threads = threads.filter(country=country_obj)
        except Country.DoesNotExist:
            pass  # Если страна не найдена, фильтрация не происходит

    # Фильтрация по категории и её подкатегориям
    category = None
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            # Получаем все подкатегории этой категории
            subcategories = category.subcategories.all()
            threads = threads.filter(category__in=[category] + list(subcategories))
        except Category.DoesNotExist:
            pass  # Если категория не найдена, фильтрация по ней не происходит

    # Добавляем аннотацию для подсчёта комментариев
    threads = threads.annotate(comments_count=Count('comments'))

    # Все активные категории для отображения в фильтре
    categories = Category.objects.filter(is_active=True)

    # Пагинация
    paginator = Paginator(threads, 5)  # 5 тредов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Заголовок страницы в зависимости от фильтрации
    if category and country_obj:
        page_title = f'Обговорення за категорією: {category.name} | Країна: {country_obj.name}'
    elif category:
        page_title = f'Обговорення за категорією: {category.name}'
    elif country_obj:
        page_title = f'Обговорення за країною: {country_obj.name}'
    else:
        page_title = "Список всіх обговорень"

    return render(request, 'forum/thread_list.html', {
        'threads': threads,
        'categories': categories,
        'countries': countries,
        'page_title': page_title,
        'page_obj': page_obj,
        'search_query': search_query,
    })


def category_list(request):
    all_categories = all_categories = Category.objects.all()

    data = {
        'all_categories': all_categories,
    }
    return render(request, 'forum/category_list.html', context=data)



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
    comments_list = thread.comments.all().order_by('-created_at')

    # Загружаем первые 25 комментариев
    # comments = comments_list[:25]

    # Преобразуем время комментариев в UTC
    comments = [
        {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),  # Время в UTC
            'avatar_url': comment.author.profile.avatar.url if hasattr(comment.author, 'profile') else '',
        }
        for comment in comments_list[:25]  # Берем первые 25 комментариев
    ]

    # Получаем общее количество комментариев
    comment_count = comments_list.count()

    latest_threads = Thread.objects.order_by('-created_at')[:7]
    popular_threads = Thread.objects.annotate(comment_count=models.Count('comments')).order_by('-comment_count')[:7]

    # if request.method == "POST":
    #     form = CommentForm(request.POST)
    #     if form.is_valid():
    #         comment = form.save(commit=False)
    #         comment.thread = thread
    #         comment.author = request.user
    #         comment.save()
    #         return redirect(thread.get_absolute_url())
    # else:
    #     form = CommentForm()

    context = {
        'thread': thread,
        'comments': comments,  # Передаем первые 25 комментариев
        'comment_count': comment_count,  # Общее количество комментариев
        # 'form': form,
        'latest_threads': latest_threads,
        'popular_threads': popular_threads,
    }
    return render(request, 'forum/thread_detail.html', context)


def load_more_comments(request, thread_slug):
    thread = get_object_or_404(Thread, slug=thread_slug)
    offset = int(request.GET.get('offset', 0))  # Количество уже загруженных комментариев
    limit = 25  # Количество комментариев для подгрузки

    # Получаем следующие 25 комментариев
    comments = thread.comments.all().order_by('-created_at')[offset:offset + limit]

    # Сериализуем комментарии
    serialized_comments = [
        {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'avatar_url': comment.author.profile.avatar.url if hasattr(comment.author, 'profile') and comment.author.profile.avatar else '',
        }
        for comment in comments
    ]

    # Рендерим HTML для новых комментариев
    comments_html = render_to_string('forum/comments_partial.html', {
        'comments': serialized_comments,
        'user': request.user,  # Передаем текущего пользователя в контекст
    })

    return JsonResponse({
        'comments_html': comments_html,
        'has_more': len(comments) == limit,  # Есть ли еще комментарии для подгрузки
    })


@csrf_exempt  # Отключаем CSRF-защиту, если это не критично
@require_POST
@login_required
def report_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        data = json.loads(request.body)
        reason = data.get('reason')
        # reason = request.POST.get('reason')

        # Проверяем, не жаловался ли уже пользователь на этот комментарий
        if Complaint.objects.filter(comment=comment, user=request.user).exists():
            return JsonResponse({'status': 'error', 'message': 'Ви вже скаржилися на цей коментар.'}, status=400)

        # Создаем запись о жалобе
        Complaint.objects.create(
            comment=comment,
            user=request.user,
            reason=reason,
            status='new'  # Статус по умолчанию
        )

        return JsonResponse({'status': 'success', 'message': 'Скаргу успішно надіслано.'})
    except Comment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Коментар не знайдено.'}, status=404)