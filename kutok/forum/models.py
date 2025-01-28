import random
import string
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL категорії")
    description = models.TextField(blank=True, null=True, verbose_name="Опис категорії")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Зображення категорії")
    is_active = models.BooleanField(default=True, verbose_name="Активна категорія")
    # parent = models.ForeignKey(
    #     'self', on_delete=models.SET_NULL, blank=True, null=True,
    #     related_name='subthreads', verbose_name="Батьківська категорія"
    # )

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("home", kwargs={"category_slug": self.slug})
    



class Thread(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва обговорення")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL обговорення", blank=True)
    
    
    content = models.TextField(verbose_name="Текст обговорення")
    category = models.ForeignKey(
        'Category', on_delete=models.PROTECT, 
        related_name='threads', verbose_name="Категорія")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    is_active = models.BooleanField(default=True, verbose_name="Активне обговорення")

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]
        verbose_name = "Обговорення"
        verbose_name_plural = "Обговорення"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Преобразуем кириллицу в латиницу
            slugified_title = unidecode(self.title)
            self.slug = slugify(slugified_title)
            
            # Если слаг уже существует, генерируем уникальный
            while Thread.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(slugified_title)}-{self.generate_random_string()}"
        
        super().save(*args, **kwargs)

    def generate_random_string(self, length=6):
        """Генерация случайной строки для обеспечения уникальности слега."""
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("forum:thread_detail", kwargs={"thread_slug": self.slug})
    



class Comment(models.Model):
    DEFAULT_ANONYMOUS_USER_ID=2

    thread = models.ForeignKey(
        'Thread', on_delete=models.CASCADE, 
        related_name='comments', verbose_name="Обговорення"
    )
    author = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, 
    default=DEFAULT_ANONYMOUS_USER_ID, verbose_name="Автор", 
    null=True, blank=True)

    content = models.TextField(verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        ordering = ['-created_at']

    def __str__(self):
        return f"Коментар від {self.author} до {self.thread}"