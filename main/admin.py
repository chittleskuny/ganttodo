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
        ('basic', {'fields': [
            'project',
            'title',
            'description',
            'reference',
            'milestone',
            'priority',
            'cost',
            'start',
            'deadline',
            'assignee',
            'status'
        ]}),
    ]
    list_display = (
        'id',
        'project',
        'title',
        'description',
        'reference',
        'milestone',
        'priority',
        'cost',
        'start',
        'deadline',
        'assignee',
        'status',
    )


class TaskPositionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['pre', 'post']}),
    ]
    list_display = ('id', 'pre', 'post',)


class CalendarAdmin(admin.ModelAdmin):
    fieldsets = [
        ('basic', {'fields': ['date', 'is_holiday']}),
    ]
    list_display = ('date', 'is_holiday',)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskPosition, TaskPositionAdmin)
admin.site.register(Calendar, CalendarAdmin)
