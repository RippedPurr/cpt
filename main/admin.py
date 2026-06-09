# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Post, Category, Product, MasterClass, ProductOrder, MasterClassRegistration


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, obj):
        return obj.profile.role

    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    fields = ('category', 'name', 'description', 'price', 'image', 'stock', 'model_3d')


@admin.register(MasterClass)
class MasterClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'price', 'max_participants', 'participants_count')
    list_filter = ('date_time',)
    search_fields = ('title', 'description')
    date_hierarchy = 'date_time'


@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'status', 'order_date')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'product__name')
    date_hierarchy = 'order_date'


@admin.register(MasterClassRegistration)
class MasterClassRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'master_class', 'registration_date', 'is_paid')
    list_filter = ('is_paid', 'registration_date')
    search_fields = ('user__username', 'master_class__title')
    date_hierarchy = 'registration_date'


