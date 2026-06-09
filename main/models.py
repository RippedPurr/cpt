from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
# Create your models here.



class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'Обычный пользователь'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name="Изображение")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Изображение")
    image1 = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    image2 = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    image3 = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    stock = models.IntegerField(default=0, verbose_name="Количество на складе")
    created_at = models.DateTimeField(auto_now_add=True)
    model_3d = models.FileField(
        upload_to='products/3d/',
        null=True,
        blank=True,
        verbose_name="3D модель",
        help_text="Поддерживаются форматы: .glb, .gltf")

    def __str__(self):
        return self.name


class MasterClass(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    image1 = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    image2 = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    image3 = models.ImageField(upload_to='master_classes/', null=True, blank=True, verbose_name="Изображение")
    date_time = models.DateTimeField(verbose_name="Дата и время проведения")
    duration = models.IntegerField(help_text="Длительность в минутах", verbose_name="Длительность")
    max_participants = models.IntegerField(default=10, verbose_name="Максимум участников")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def participants_count(self):
        return self.registrations.count()

    def available_slots(self):
        return self.max_participants - self.participants_count()



class ProductOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтвержден'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Заказ {self.id} - {self.user.username} - {self.product.name}"

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)


class MasterClassRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='masterclass_registrations')
    master_class = models.ForeignKey(MasterClass, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'master_class']

    def __str__(self):
        return f"{self.user.username} - {self.master_class.title}"