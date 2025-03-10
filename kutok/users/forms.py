import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate



class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="username",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Введіть ваш Ник-нейм",
            'id': 'username',
        })
    )
    password = forms.CharField(
        label='Пароль',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть ваш пароль',
            'type': 'password',
            'id': 'password',
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        User = get_user_model()  # Получаем модель пользователя
        # Проверка, существует ли пользователь с таким именем
        if not User.objects.filter(username=username).exists():
            raise ValidationError("Користувач з таким ім'ям не існує.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Проверка на минимальную длину пароля
        if len(password) < 8:
            raise ValidationError("Пароль повинен містити хоча б 8 символів.")
        # Проверка на наличие хотя бы одной заглавной буквы
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль повинен містити щонайменше одну велику літеру.")
        # Проверка на наличие хотя бы одной цифры
        if not re.search(r'[0-9]', password):
            raise ValidationError("Пароль повинен містити хоча б одну цифру.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Здесь мы проверяем, существует ли пользователь с данным логином и паролем
        if username and password:
            User = get_user_model()
            user = User.objects.filter(username=username).first()
            if user and not user.check_password(password):
                raise ValidationError("Невірний пароль.")
        return cleaned_data
        
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     username = cleaned_data.get('username')
    #     password = cleaned_data.get('password')

    #     # Дополнительная проверка правильности пары логин/пароль
    #     if username and password:
    #         user = authenticate(username=username, password=password)
    #         if user is None:
    #             raise ValidationError("Невірне ім'я користувача або пароль.")
    #     return cleaned_data


class RegistrationForm(forms.Form):

    

    username = forms.CharField(
        min_length=3,
        max_length=15,
        label="Iм'я користувача",
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Введіть ваше ім'я користувача",
            'type': 'text',
            'id': 'username',
        })
    )
    email = forms.EmailField(
        max_length=100,
        label='Email', 
        required=True, 
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "Введіть вашу електронну пошту",
            'type': 'email',
            'id': 'email',
        })
    )
    password = forms.CharField(
        label='Пароль',
        required=True, 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Введіть пароль",
            'type': 'password',
            'id': 'password',
        })
    )
    confirm_password = forms.CharField(
        label='Підтвердження пароля',
        required=True, 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Підтвердіть пароль",
            'type': 'password',
            'id': 'confirm-password',
        })
    )

    def clean_username(self):
        FORBIDDEN_USERNAMES = ['admin', 'moderator', 'support']

        username = self.cleaned_data.get('username')

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Нікнейм може містити лише літери, цифри та підкреслення.")
        
        if User.objects.filter(username=username).exists():
            raise ValidationError("Цей нікнейм уже зайнятий. Виберіть інший.")
        
        if username in FORBIDDEN_USERNAMES:
            raise ValidationError("Цей нікнейм зарезервований. Виберіть інший.")
        return username
    
    
    def clean_email(self):
        # Проверяем, есть ли уже такой email в базе
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return email


    def clean_password(self):
        password = self.cleaned_data.get('password')
        # username = self.cleaned_data.get('username')

        if len(password) < 8:
            raise ValidationError("Пароль повинен містити щонайменше 8 символів.")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль повинен містити щонайменше одну велику літеру.")

        if not re.search(r'[0-9]', password):
            raise ValidationError("Пароль повинен містити хоча б одну цифру.")
        
        # if username.lower() == password.lower():
        #     raise ValidationError("Пароль не повинен містити ваше ім'я користувача.")
        
        # if email.split('@')[0].lower() == password.lower():
        #     raise ValidationError("Пароль не повинен містити частину вашої електронної пошти.")

        return password
    

    def clean_confirm_password(self):
        # Проверка, что пароли совпадают
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Пароли не совпадают.")
        return confirm_password
    

class CustomPasswordResetForm(PasswordResetForm):
    
    email = forms.EmailField(
        max_length=100,
        label='Електронна пошта', 
        required=True, 
        validators=[EmailValidator],  # Свое сообщение
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "Введіть вашу електронну пошту",
            'type': 'email',
            'id': 'email',
        })
    )
    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Проверяем, существует ли пользователь с таким email
        User = get_user_model()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувача з такою електронною поштою не знайдено.")

        return email
    

class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть новий пароль'
        })
    )
    new_password2 = forms.CharField(
        label='Підтвердження нового пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердіть новий пароль'
        })
    )
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")

        if len(new_password1) < 8:
            raise ValidationError("Пароль повинен містити щонайменше 8 символів.")

        if not re.search(r'[A-Z]', new_password1):
            raise ValidationError("Пароль повинен містити щонайменше одну велику літеру.")

        if not re.search(r'[0-9]', new_password1):
            raise ValidationError("Пароль повинен містити хоча б одну цифру.")
        
        return new_password1


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Поточний пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть ваш поточний пароль'
        }),
        error_messages={
            # 'required': 'Будь ласка, введіть поточний пароль.',
        }
    )

    new_password1 = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть новий пароль'
        }),
        error_messages={
            'required': 'Будь ласка, введіть новий пароль.',
            'min_length': 'Пароль має бути не менше 8 символів.',
        }
    )

    new_password2 = forms.CharField(
        label='Підтвердження пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердіть новий пароль'
        }),
        error_messages={
            'required': 'Будь ласка, підтвердіть новий пароль.',
            # 'match': 'Паролі не співпадають. Спробуйте ще раз.',
        }
    )

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):  # Проверяем старый пароль
            raise forms.ValidationError("Ваш поточний пароль введено некоректно. Будь ласка, спробуйте ще раз.")
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        
        if new_password1 != new_password2:
            raise forms.ValidationError("Паролі не співпадають. Спробуйте ще раз.")
        
        return new_password2
    
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        old_password = self.cleaned_data.get("old_password")
        # username = self.cleaned_data.get('username')

        if new_password1 == old_password:
            raise forms.ValidationError("Новий пароль має відрізнятися від старого")
        
        if len(new_password1) < 8:
            raise ValidationError("Пароль повинен містити щонайменше 8 символів.")

        if not re.search(r'[A-Z]', new_password1):
            raise ValidationError("Пароль повинен містити щонайменше одну велику літеру.")

        if not re.search(r'[0-9]', new_password1):
            raise ValidationError("Пароль повинен містити хоча б одну цифру.")
        
        # if username.lower() == password.lower():
        #     raise ValidationError("Пароль не повинен містити ваше ім'я користувача.")
        
        # if email.split('@')[0].lower() == password.lower():
        #     raise ValidationError("Пароль не повинен містити частину вашої електронної пошти.")

        return new_password1
