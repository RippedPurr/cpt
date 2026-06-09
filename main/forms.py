from datetime import timezone

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, ProductOrder, MasterClassRegistration, MasterClass, Profile, Product, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, label="Имя",
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, label="Телефон",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', ''),
                role='user'
            )
        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'emoji-textarea form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'image': 'Изображение',
            'is_published': 'Опубликовать сразу',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название категории',
            'slug': 'URL-идентификатор',
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'image', 'image1', 'image2', 'image3', 'stock', 'model_3d']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image1': forms.FileInput(attrs={'class': 'form-control'}),
            'image2': forms.FileInput(attrs={'class': 'form-control'}),
            'image3': forms.FileInput(attrs={'class': 'form-control'}),
            'model_3d': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'category': 'Категория',
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена (₽)',
            'image': 'Изображение',
            'stock': 'Количество на складе',
        }


class MasterClassForm(forms.ModelForm):
    class Meta:
        model = MasterClass
        fields = ['title', 'description', 'price', 'image', 'image1', 'image2', 'image3', 'date_time', 'duration', 'max_participants']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image1': forms.FileInput(attrs={'class': 'form-control'}),
            'image2': forms.FileInput(attrs={'class': 'form-control'}),
            'image3': forms.FileInput(attrs={'class': 'form-control'}),
            'date_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название мастер-класса',
            'description': 'Описание',
            'price': 'Цена (₽)',
            'image': 'Изображение',
            'date_time': 'Дата и время проведения',
            'duration': 'Длительность (минут)',
            'max_participants': 'Максимальное количество участников',
        }



class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = ProductOrder
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class MasterClassRegistrationForm(forms.ModelForm):
    class Meta:
        model = MasterClassRegistration
        fields = ['master_class']
        widgets = {
            'master_class': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['master_class'].queryset = MasterClass.objects.filter(
            date_time__gt=timezone.now()
        ).order_by('date_time')
        self.fields['master_class'].label_from_instance = lambda \
            obj: f"{obj.title} - {obj.date_time.strftime('%d.%m.%Y %H:%M')}"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }