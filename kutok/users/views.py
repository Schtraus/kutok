from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, CustomUsernameChangeForm, RegistrationForm, CustomPasswordResetConfirmForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth import update_session_auth_hash


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
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Проверка, какой именно запрос был отправлен
        if "username" in request.POST:
            form = CustomUsernameChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
        elif "old_password" in request.POST:
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    
    username_form = CustomUsernameChangeForm(request.user)
    password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/profile.html', {'username_form': username_form, 'password_form': password_form})


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