from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import *


class CustomUserAdmin(UserAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('email', 'role', 'is_approved', 'is_active')
    list_filter = ('role', 'is_approved', 'is_active')  # Add filters for role and approval status
    search_fields = ('email',)  # Allow searching by email
    ordering = ('email',)  # Order by email
    
    # Customizing the fields in the admin form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role', 'is_approved')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_approved', 'is_active'),
        }),
    )

# Register your models here.
admin.site.register(CustomUser,CustomUserAdmin)