from django.contrib import admin

from .models import *


# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['name']}),
    ]
    list_display = ('id', 'name',)


class TaskAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['project', 'title', 'description', 'reference', 'priority', 'cost', 'deadline']}),
    ]
    list_display = ('id', 'project', 'title', 'description', 'reference', 'priority', 'cost', 'deadline',)


class CalendarAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['date', 'is_holiday']}),
    ]
    list_display = ('date', 'is_holiday',)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Calendar, CalendarAdmin)
