from django.contrib import admin
from .models import UserProfile, EmailOTP, Campaign, Candidate, Vote
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin



admin.site.register(UserProfile)
admin.site.register(EmailOTP)
admin.site.register(Campaign)
admin.site.register(Candidate)
admin.site.register(Vote)

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
