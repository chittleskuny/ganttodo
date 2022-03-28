from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic

from .models import *

# Create your views here.

class IndexView(generic.base.TemplateView):
    template_name = 'main/index.html'


class TaskListView(generic.ListView):
    model = Task
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Task.objects.order_by('id')


class TaskDetailView(generic.DetailView):
    model = Task
    context_object_name = 'task'


class TaskCreateView(generic.CreateView):
    model = Task
    fields = ['title', 'description', 'reference', 'priority', 'cost', 'deadline']
    template_name = 'main/create.html'


class TaskUpdateView(generic.UpdateView):
    model = Task
    fields = ['title', 'description', 'reference', 'priority', 'cost', 'deadline']
    template_name = 'main/update.html'


class TaskDeleteView(generic.DeleteView):
    model = Task
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:task_list')


class CalendarListView(generic.ListView):
    model = Calendar
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Calendar.objects.order_by('date')


class CalendarDetailView(generic.DetailView):
    model = Calendar
    context_object_name = 'calendar'


class CalendarCreateView(generic.CreateView):
    model = Calendar
    fields = ['date', 'is_holiday']
    template_name = 'main/create.html'


class CalendarUpdateView(generic.UpdateView):
    model = Calendar
    fields = ['date', 'is_holiday']
    template_name = 'main/update.html'


class CalendarDeleteView(generic.DeleteView):
    model = Calendar
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:calendar_list')
