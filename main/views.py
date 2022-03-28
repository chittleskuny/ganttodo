from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic

from .models import *

import json
import datetime, time


# Create your views here.


today = 1000 * int(time.mktime(datetime.date.today().timetuple()))
day = 1000 * 60 * 60 * 24


class IndexView(generic.base.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, *args, **kwargs):
        context = {}
        series_object = [
            {
                'name': 'Offices',
                'data': [
                    {
                        'name': 'New offices',
                        'id': 'new_offices',
                        'owner': 'Peter'
                    }, {
                        'name': 'Prepare office building',
                        'id': 'prepare_building',
                        'parent': 'new_offices',
                        'start': today - (2 * day),
                        'end': today + (6 * day),
                        'completed': {
                            'amount': 0.2
                        },
                        'owner': 'Linda'
                    }, {
                        'name': 'Inspect building',
                        'id': 'inspect_building',
                        'dependency': 'prepare_building',
                        'parent': 'new_offices',
                        'start': today + 6 * day,
                        'end': today + 8 * day,
                        'owner': 'Ivy'
                    }, {
                        'name': 'Passed inspection',
                        'id': 'passed_inspection',
                        'dependency': 'inspect_building',
                        'parent': 'new_offices',
                        'start': today + 9.5 * day,
                        'milestone': True,
                        'owner': 'Peter'
                    }, {
                        'name': 'Relocate',
                        'id': 'relocate',
                        'dependency': 'passed_inspection',
                        'parent': 'new_offices',
                        'owner': 'Josh'
                    }, {
                        'name': 'Relocate staff',
                        'id': 'relocate_staff',
                        'parent': 'relocate',
                        'start': today + 10 * day,
                        'end': today + 11 * day,
                        'owner': 'Mark'
                    }, {
                        'name': 'Relocate test facility',
                        'dependency': 'relocate_staff',
                        'parent': 'relocate',
                        'start': today + 11 * day,
                        'end': today + 13 * day,
                        'owner': 'Anne'
                    }, {
                        'name': 'Relocate cantina',
                        'dependency': 'relocate_staff',
                        'parent': 'relocate',
                        'start': today + 11 * day,
                        'end': today + 14 * day
                    }
                ]
            }, {
                'name': 'Product',
                'data': [
                    {
                        'name': 'New product launch',
                        'id': 'new_product',
                        'owner': 'Peter'
                    }, {
                        'name': 'Development',
                        'id': 'development',
                        'parent': 'new_product',
                        'start': today - day,
                        'end': today + (11 * day),
                        'completed': {
                            'amount': 0.6,
                            'fill': '#e80'
                        },
                        'owner': 'Susan'
                    }, {
                        'name': 'Beta',
                        'id': 'beta',
                        'dependency': 'development',
                        'parent': 'new_product',
                        'start': today + 12.5 * day,
                        'milestone': True,
                        'owner': 'Peter'
                    }, {
                        'name': 'Final development',
                        'id': 'finalize',
                        'dependency': 'beta',
                        'parent': 'new_product',
                        'start': today + 13 * day,
                        'end': today + 17 * day
                    }, {
                        'name': 'Launch',
                        'dependency': 'finalize',
                        'parent': 'new_product',
                        'start': today + 17.5 * day,
                        'milestone': True,
                        'owner': 'Peter'
                    }
                ]
            }
        ]
        context['series'] = json.dumps(series_object)
        return super().get_context_data(**context)


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
