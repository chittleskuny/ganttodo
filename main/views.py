from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic

from .models import *

import json
import datetime, time


# Create your views here.


today = 1000 * int(time.mktime(datetime.date.today().timetuple()))
day = 1000 * 60 * 60 * 24
unit = day // 2 # TODO


def get_last_task_object(task_objects, taskposition_objects):
    for task_object in task_objects:
        for taskposition_object in taskposition_objects:
            if task_object == taskposition_object.pre:
                break
        else:
            return task_object
    else:
        return None


def remove_task_object_from_taskposition_objects(task_object, taskposition_objects):
    to_remove = []
    for taskposition_object in taskposition_objects:
        if task_object == taskposition_object.pre or task_object == taskposition_object.post:
            to_remove.append(taskposition_object)
    for taskposition_object in to_remove:
        taskposition_objects.remove(taskposition_object)
    return taskposition_objects


def get_series_object():
    user_curday = {'nobody': today}
    user_objects = User.objects.all()
    for user_object in user_objects:
        user_curday[user_object.name] = today

    series_object_dict = {}
    project_objects = Project.objects.all()
    for project_object in project_objects:
        series_object_dict[project_object.name] = {
            'name': project_object.name,
            'data': [],
        }

    task_objects_toposorted_list = []
    task_objects = list(Task.objects.filter(status=0).order_by('priority'))
    taskposition_objects = list(TaskPosition.objects.all())
    while task_objects:
        last_task_object = get_last_task_object(task_objects, taskposition_objects)
        task_objects_toposorted_list.append(last_task_object)
        task_objects.remove(last_task_object)
        taskposition_objects = remove_task_object_from_taskposition_objects(last_task_object, taskposition_objects)
    task_objects_toposorted_list.reverse()

    for task_object in task_objects_toposorted_list:
        series_project_task_object = {
            'id': str(task_object.id),
            'name': '#%s %s' % (task_object.id, task_object.title),
        }

        username = 'nobody'
        if task_object.assignee is not None:
            username = task_object.assignee.name
            series_project_task_object['owner'] = username

        series_project_task_object['start'] = user_curday[username]
        if task_object.cost != 0:
            user_curday[username] = user_curday[username] + unit * task_object.cost
            series_project_task_object['end'] = user_curday[username]
        
        if task_object.project is not None:
            series_object_dict[task_object.project.name]['data'].append(series_project_task_object)

    series_object_list = []
    for key, value in series_object_dict.items():
        series_object_list.append(value)
    return series_object_list


class IndexView(generic.base.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, *args, **kwargs):
        context = {}
        series_object = get_series_object()
        context['series'] = json.dumps(series_object)
        return super().get_context_data(**context)


class UserListView(generic.ListView):
    model = User
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return User.objects.order_by('id')


class UserDetailView(generic.DetailView):
    model = User
    context_object_name = 'user'


class UserCreateView(generic.CreateView):
    model = User
    fields = ['name']
    template_name = 'main/create.html'


class UserUpdateView(generic.UpdateView):
    model = User
    fields = ['name']
    template_name = 'main/update.html'


class UserDeleteView(generic.DeleteView):
    model = User
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:user_list')


class ProjectListView(generic.ListView):
    model = Project
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Project.objects.order_by('id')


class ProjectDetailView(generic.DetailView):
    model = Project
    context_object_name = 'project'


class ProjectCreateView(generic.CreateView):
    model = Project
    fields = ['name']
    template_name = 'main/create.html'


class ProjectUpdateView(generic.UpdateView):
    model = Project
    fields = ['name']
    template_name = 'main/update.html'


class ProjectDeleteView(generic.DeleteView):
    model = Project
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:project_list')


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
    fields = ['project', 'title', 'description', 'reference', 'priority', 'cost', 'deadline', 'assignee', 'status']
    template_name = 'main/create.html'


class TaskUpdateView(generic.UpdateView):
    model = Task
    fields = ['project', 'title', 'description', 'reference', 'priority', 'cost', 'deadline', 'assignee', 'status']
    template_name = 'main/update.html'


class TaskDeleteView(generic.DeleteView):
    model = Task
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:task_list')


class TaskPositionListView(generic.ListView):
    model = TaskPosition
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return TaskPosition.objects.order_by('id')


class TaskPositionDetailView(generic.DetailView):
    model = TaskPosition
    context_object_name = 'taskposition'


class TaskPositionCreateView(generic.CreateView):
    model = TaskPosition
    fields = ['pre', 'post']
    template_name = 'main/create.html'


class TaskPositionUpdateView(generic.UpdateView):
    model = TaskPosition
    fields = ['pre', 'post']
    template_name = 'main/update.html'


class TaskPositionDeleteView(generic.DeleteView):
    model = TaskPosition
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:taskposition_list')


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
