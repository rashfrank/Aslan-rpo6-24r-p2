from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Ad, Review, Profile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Телефон",
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (___) ___-__-__',
            'class': 'form-control'
        }),
        help_text="Укажите номер телефона, чтобы покупатели могли вам позвонить"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # Создаём профиль и сохраняем телефон
            Profile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', '').strip()
            )
        return user


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['category', 'city', 'title', 'description', 'price', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Подробно опишите товар или услугу...'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Ваш отзыв...',
                'class': 'form-control'
            }),
        }


# Дополнительная форма для редактирования профиля (полезно в будущем)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите немного о себе...'}),
        }