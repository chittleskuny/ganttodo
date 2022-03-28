from django.contrib import admin

from .models import *


# Register your models here.


class TaskAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['title', 'description', 'reference', 'priority', 'cost', 'deadline']}),
    ]
    list_display = ('id', 'title', 'description', 'reference', 'priority', 'cost', 'deadline',)


class CalendarAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['date', 'is_holiday']}),
    ]
    list_display = ('date', 'is_holiday',)


admin.site.register(Task, TaskAdmin)
admin.site.register(Calendar, CalendarAdmin)
