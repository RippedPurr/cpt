from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from django import forms

from . import forms
from .models import (
    Post, Category, Product, MasterClass,
    ProductOrder, MasterClassRegistration, User, Profile
)
from .forms import (
    RegisterForm, PostForm, ProductOrderForm,
    ProfileForm,
    ProductForm, MasterClassForm, CategoryForm
)
from .decorators import admin_required


def index(request):
    """Главная страница с постами"""
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    upcoming_masterclasses = MasterClass.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')[:5]

    context = {
        'posts': posts,
        'upcoming_masterclasses': upcoming_masterclasses,
        'title': 'Главная'
    }
    return render(request, 'index.html', context)


def catalog(request):
    """Страница каталога товаров"""
    categories = Category.objects.all().prefetch_related('products')
    context = {
        'categories': categories,
        'title': 'Каталог',
        'is_admin': request.user.is_authenticated and request.user.profile.role == 'admin'
    }
    return render(request, 'catalog.html', context)


def master_classes(request):
    upcoming_classes = MasterClass.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')
    past_classes = MasterClass.objects.filter(
        date_time__lt=timezone.now()
    ).order_by('-date_time')[:5]

    context = {
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes,
        'title': 'Мастер-классы',
        'is_admin': request.user.is_authenticated and request.user.profile.role == 'admin'
    }
    return render(request, 'master_classes.html', context)


def organization(request):
    context = {
        'title': 'Для организаций'
    }
    return render(request, 'organization.html', context)


@login_required
def signup_masterclass(request):
    master_classes = MasterClass.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')

    user_registrations = MasterClassRegistration.objects.filter(
        user=request.user
    ).values_list('master_class_id', flat=True)

    user_registrations_details = MasterClassRegistration.objects.filter(
        user=request.user
    ).select_related('master_class').order_by('-master_class__date_time')

    if request.method == 'POST':
        master_class_id = request.POST.get('master_class')
        if master_class_id:
            master_class = get_object_or_404(MasterClass, id=master_class_id)

            existing = MasterClassRegistration.objects.filter(
                user=request.user,
                master_class=master_class
            ).exists()

            if existing:
                messages.error(request, 'Вы уже записаны на этот мастер-класс')
            elif master_class.available_slots() <= 0:
                messages.error(request, 'На этот мастер-класс нет свободных мест')
            else:
                registration = MasterClassRegistration.objects.create(
                    user=request.user,
                    master_class=master_class
                )
                messages.success(request, f'Вы успешно записаны на мастер-класс "{master_class.title}"')
                return redirect('signup')
        else:
            messages.error(request, 'Пожалуйста, выберите мастер-класс')

    context = {
        'master_classes': master_classes,
        'user_registrations': user_registrations,
        'user_registrations_details': user_registrations_details,
        'now': timezone.now(),
        'title': 'Запись на мастер-классы'
    }
    return render(request, 'signup.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
    else:
        form = RegisterForm()

    context = {
        'form': form,
        'title': 'Регистрация'
    }
    return render(request, 'register.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')

            try:
                profile = user.profile
            except Profile.DoesNotExist:
                Profile.objects.create(user=user, role='user')

            return redirect('index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    context = {
        'title': 'Вход'
    }
    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')


@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user, role='user')

    is_admin = profile.role == 'admin'

    if request.method == 'POST' and not is_admin:
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile) if not is_admin else None

    if is_admin:
        today = timezone.now().date()
        week_from_now = today + timedelta(days=7)

        upcoming_masterclasses = MasterClass.objects.filter(
            date_time__date__gte=today,
            date_time__date__lte=week_from_now
        ).order_by('date_time')

        recent_orders = ProductOrder.objects.filter(
            status='pending'
        ).select_related('user', 'product')[:10]

        total_users = User.objects.count()
        total_orders = ProductOrder.objects.count()
        total_registrations = MasterClassRegistration.objects.count()
        total_products = Product.objects.count()
        total_masterclasses = MasterClass.objects.count()
        total_posts = Post.objects.count()

        recent_posts = Post.objects.order_by('-created_at')[:5]
        recent_products = Product.objects.order_by('-created_at')[:5]
        recent_masterclasses = MasterClass.objects.order_by('-created_at')[:5]

        context = {
            'is_admin': True,
            'upcoming_masterclasses': upcoming_masterclasses,
            'recent_orders': recent_orders,
            'total_users': total_users,
            'total_orders': total_orders,
            'total_registrations': total_registrations,
            'total_products': total_products,
            'total_masterclasses': total_masterclasses,
            'total_posts': total_posts,
            'recent_posts': recent_posts,
            'recent_products': recent_products,
            'recent_masterclasses': recent_masterclasses,
            'title': 'Панель администратора'
        }
    else:
        user_registrations = MasterClassRegistration.objects.filter(
            user=user
        ).select_related('master_class').order_by('-master_class__date_time')

        user_orders = ProductOrder.objects.filter(
            user=user
        ).select_related('product').order_by('-order_date')

        context = {
            'is_admin': False,
            'profile_form': profile_form,
            'registrations': user_registrations,
            'orders': user_orders,
            'title': 'Личный кабинет'
        }

    return render(request, 'profile.html', context)


@admin_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно опубликован!')
            return redirect('index')
    else:
        form = PostForm()

    context = {
        'form': form,
        'title': 'Новый пост'
    }
    return render(request, 'add_post.html', context)


@admin_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен')
            return redirect('index')
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'title': 'Редактирование поста'
    }
    return render(request, 'add_post.html', context)


@admin_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    messages.success(request, 'Пост удален')
    return redirect('index')


@admin_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана')
            return redirect('catalog')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'title': 'Новая категория'
    }
    return render(request, 'admin_forms/category_form.html', context)


@admin_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена')
            return redirect('catalog')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'title': 'Редактирование категории'
    }
    return render(request, 'admin_forms/category_form.html', context)


@admin_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if category.products.exists():
        messages.error(request, 'Нельзя удалить категорию, в которой есть товары')
    else:
        category.delete()
        messages.success(request, 'Категория удалена')
    return redirect('catalog')


@admin_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно добавлен')
            return redirect('catalog')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'title': 'Новый товар'
    }
    return render(request, 'admin_forms/product_form.html', context)


@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар обновлен')
            return redirect('catalog')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'title': 'Редактирование товара'
    }
    return render(request, 'admin_forms/product_form.html', context)


@admin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Товар удален')
    return redirect('catalog')


@admin_required
def add_masterclass(request):
    if request.method == 'POST':
        form = MasterClassForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Мастер-класс успешно создан')
            return redirect('master_classes')
    else:
        form = MasterClassForm()

    context = {
        'form': form,
        'title': 'Новый мастер-класс'
    }
    return render(request, 'admin_forms/masterclass_form.html', context)


@admin_required
def edit_masterclass(request, masterclass_id):
    masterclass = get_object_or_404(MasterClass, id=masterclass_id)

    if request.method == 'POST':
        form = MasterClassForm(request.POST, request.FILES, instance=masterclass)
        if form.is_valid():
            form.save()
            messages.success(request, 'Мастер-класс обновлен')
            return redirect('master_classes')
    else:
        form = MasterClassForm(instance=masterclass)

    context = {
        'form': form,
        'masterclass': masterclass,
        'title': 'Редактирование мастер-класса'
    }
    return render(request, 'admin_forms/masterclass_form.html', context)


@admin_required
def delete_masterclass(request, masterclass_id):
    masterclass = get_object_or_404(MasterClass, id=masterclass_id)
    masterclass.delete()
    messages.success(request, 'Мастер-класс удален')
    return redirect('master_classes')


@admin_required
def order_masterclass_participants(request, masterclass_id):
    masterclass = get_object_or_404(MasterClass, id=masterclass_id)
    registrations = masterclass.registrations.select_related('user').all()

    participants = [{
        'name': f"{reg.user.last_name} {reg.user.first_name}",
        'email': reg.user.email,
        'phone': reg.user.profile.phone if hasattr(reg.user, 'profile') else '',
        'registered': reg.registration_date.strftime('%d.%m.%Y %H:%M'),
        'paid': reg.is_paid
    } for reg in registrations]

    return JsonResponse({
        'masterclass': masterclass.title,
        'participants': participants,
        'count': len(participants)
    })


@admin_required
def order_details(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)

    data = {
        'order_id': order.id,
        'user': f"{order.user.last_name} {order.user.first_name}",
        'email': order.user.email,
        'phone': order.user.profile.phone if hasattr(order.user, 'profile') else '',
        'product': order.product.name,
        'quantity': order.quantity,
        'total_price': float(order.total_price),
        'order_date': order.order_date.strftime('%d.%m.%Y %H:%M'),
        'status': order.get_status_display()
    }

    return JsonResponse(data)


@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductOrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > product.stock:
                messages.error(request, 'Недостаточно товара на складе')
            else:
                order = ProductOrder.objects.create(
                    user=request.user,
                    product=product,
                    quantity=quantity,
                    total_price=product.price * quantity
                )
                product.stock -= quantity
                product.save()
                messages.success(request, f'Товар "{product.name}" добавлен в корзину')
                return redirect('catalog')
    else:
        form = ProductOrderForm(initial={'quantity': 1})

    context = {
        'form': form,
        'product': product,
        'title': f'Покупка: {product.name}'
    }
    return render(request, 'buy_product.html', context)


def product_detail(request, product_id):
    """Страница отдельного товара"""
    product = get_object_or_404(Product, id=product_id)
    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'similar_products': similar_products,
        'title': product.name
    }
    return render(request, 'product_detail.html', context)