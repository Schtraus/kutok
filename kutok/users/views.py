from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, RegistrationForm, CustomPasswordResetConfirmForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


# def login_view(request):
#     user = None
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request,
#                 username=cd['username'],
#                 password=cd['password'])
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponse('Authenticated successfully')
#             else:
#                 return HttpResponse('Disabled account')
#         else:
#             return HttpResponse('Invalid login')
#     else:
#         form = LoginForm()
#     return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Создание нового пользователя
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, email=email, password=password)

            # Логиним пользователя после регистрации
            login(request, user)

            # Отправляем сообщение об успехе
            messages.success(request, "Вы успешно зарегистрированы!")

            return redirect('/')  # Перенаправляем на главную страницу
        else:
            # Если форма не валидна, выводим ошибки
            messages.error(request, "Ошибка при регистрации. Пожалуйста, попробуйте снова.")
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html')


class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordConfirmView(auth_views.PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')