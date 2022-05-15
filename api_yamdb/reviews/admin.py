from django.contrib import admin

from .models import Review, Comment, Category, Genre, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role',
                    'first_name', 'last_name', 'bio')
    list_editable = ('role',)
    search_fields = ('username',)
    empty_value_display = '-пусто-'
    ordering = ['-username']


admin.site.register(User, UserAdmin)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
