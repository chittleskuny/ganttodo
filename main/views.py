from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic

from .models import *
from .forms import *
from .algorithms.default import *

import re
import json
import logging
import chinese_calendar


def update_task_objects(user):
    last_zero = datetime(
        year=date.today().year,
        month=date.today().month,
        day=date.today().day,
        tzinfo=LOCAL_TIME_ZONE_INFO,
    )

    refresh = False

    doing_serie_objects = list(Serie.objects
        .filter(task__user=user)
        .filter(task__status=STATUS_CHOICE_STR_LIST.index('Doing'))
        .filter(end__lte=timezone.now())
    )
    for serie_object in doing_serie_objects:
        logging.debug('serie_object: %s' % serie_object)

        task_object = Task.objects.get(pk=serie_object.task.id)
        logging.debug('task_object: %s' % task_object)

        delta_units_from_last_zero = get_delta_units_from_last_zero()
        task_object.cost = (last_zero + delta_units_from_last_zero - serie_object.start) // UNIT
        task_object.save()

        refresh = True
        logging.debug('Need to refresh.')

    if refresh:

        refresh_serie_objects(user)

    else:

        todo_serie_objects = list(Serie.objects
            .filter(task__user=user)
            .filter(task__status=STATUS_CHOICE_STR_LIST.index('Todo'))
            .filter(start__lte=timezone.now())
        )
        for serie_object in todo_serie_objects:
            logging.debug('serie_object: %s' % serie_object)

            task_object = Task.objects.get(pk=serie_object.task.id)
            logging.debug('task_object: %s' % task_object)
            
            if serie_object.start <= timezone.now() and task_object.status == STATUS_CHOICE_STR_LIST.index('Todo'):
                task_object.start = serie_object.start
                task_object.status = STATUS_CHOICE_STR_LIST.index('Doing')
                task_object.save()


def get_series(user):
    serie_object_dict = {
        '0': {
            'name': 'Others',
            'data': [],
        }
    }

    group_objects = user.groups.all().order_by('name')
    logging.debug('group_objects: %s' % group_objects)

    project_objects = list(Project.objects.filter(group__in=group_objects))
    project_objects.append(None)
    logging.debug('project_objects: %s' % project_objects)

    for project_object in project_objects:
        logging.debug('project_object: %s' % project_object)

        serie_objects = Serie.objects.filter(task__project=project_object)
        logging.debug('serie_objects: %s' % serie_objects)

        for serie_object in serie_objects:
            task_object = serie_object.task
            task_object_user = None
            if task_object.user is not None:
                task_object_user = task_object.user.username
            serie_project_task_obect = {
                'id': 'task_%d' % task_object.id,
                'name': str(task_object),
                'milestone': task_object.milestone,
                'user': task_object_user,
                'status': task_object.status,
                'start': convert_datetime_to_timestamp(serie_object.start),
                'end': convert_datetime_to_timestamp(serie_object.end - timedelta(seconds=1)),
            }

            project_object = serie_object.task.project

            if project_object is not None:
                if str(project_object.id) not in serie_object_dict:
                    serie_object_dict[str(project_object.id)] = {
                        'name': project_object.name,
                        'data': [
                            {
                                'id': 'project_%d' % project_object.id,
                                'name': project_object.name,
                            }
                        ],
                    }

                serie_project_task_obect['parent'] = 'project_%d' % project_object.id,
                serie_object_dict[str(project_object.id)]['data'].append(serie_project_task_obect)

            else:
                serie_object_dict[str(0)]['data'].append(serie_project_task_obect)

    serie_object_list = []
    for key, value in serie_object_dict.items():
        serie_object_list.append(value)
    
    return serie_object_list


def more_calendars():
    i_from = 0
    i_to = 100

    last_calendar_object = Calendar.objects.last()
    if last_calendar_object is not None:
        i_from = abs(Calendar.objects.last().date - date.today()) // ONE_DAY + 1
        i_to = 100

    if i_from < i_to:
        logging.info('More calendars: (%d, %d)' % (i_from, i_to))
        for i in range(i_from, i_to):
            i_date = datetime.today() + ONE_DAY * i
            calendar_object = Calendar(
                date = i_date,
                is_holiday = chinese_calendar.is_holiday(i_date)
            )
            calendar_object.save()


class IndexView(LoginRequiredMixin, generic.base.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, *args, **kwargs):
        context = {}

        update_task_objects(self.request.user)
        context['series'] = json.dumps(get_series(self.request.user))

        return super().get_context_data(**context)


@login_required
def accounts_profile(request):
    more_calendars()
    groups = list(request.user.groups.all().order_by('name'))
    user_permissions = list(request.user.user_permissions.all())
    return render(request, 'main/accounts_profile.html', {
        'user': request.user,
        'groups': groups,
        'user_permissions': user_permissions,
    })


def accounts_login(request):
    return render(request, 'main/accounts_login.html')


def accounts_login_submit(request):
    username = request.POST.get('username').strip()
    password = request.POST.get('password').strip()

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('main:index'))
    else:
        return HttpResponseRedirect(reverse('main:accounts_login'))


@login_required
def accounts_logout_submit(request):
    logout(request)
    return HttpResponseRedirect(reverse('main:index'))


def accounts_refresh_submit(request):
    refresh_serie_objects(request.user)
    return HttpResponseRedirect(reverse('main:index'))


def group_list(request):
    return render(request, 'main/group_list.html', {
        'queryset_list': request.user.groups.all().order_by('name'),
    })


def group_detail(request, pk):
    group_object = Group.objects.get(pk=pk)
    user_objects = group_object.user_set.order_by('username')
    project_objects = Project.objects.filter(group__pk=pk).order_by('-id')

    return render(request, 'main/group_detail.html', {
        'user_objects': user_objects,
        'project_objects': project_objects,
    })


def group_project_create(request, pk):
    group_object = Group.objects.get(pk=pk)
    initial = {'group': group_object}
    project_form = ProjectFrom(initial=initial)

    return render(request, 'main/project_create_or_update.html', {
        'form': project_form,
    })


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Project.objects.order_by('name')


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    context_object_name = 'project'

    def get_context_data(self, *args, **kwargs):
        context = {}

        if self.object:
            project_object = self.object
            task_objects = Task.objects.filter(project=project_object).order_by('-id')
            context['task_objects'] = task_objects

        return super().get_context_data(**context)


def project_create_or_update_submit(request):
    group = request.POST.get('group').strip()
    name = request.POST.get('name').strip()

    group_object = None if group == '' else Group.objects.get(pk=int(group))

    name = 'Untitled' if name == '' else name

    project_object = Project(
        group = group_object,
        name = name,
    )
    project_object.save()

    return HttpResponseRedirect(reverse('main:project_detail', args=(project_object.pk,)))


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    template_name = 'main/create_or_update.html'
    success_url = reverse_lazy('main:project_detail')


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:project_list')


def project_task_list(request, pk):
    project_object = Project.objects.get(pk=pk)

    task_objects = Task.objects.filter(project=project_object).order_by('-id')

    return render(request, 'main/task_list.html', {
        'task_objects': task_objects,
    })


def project_task_create(request, pk):
    specified_project_object = Project.objects.get(pk=pk)
    group_object = specified_project_object.group
    user_objects = User.objects.filter(groups__name=group_object.name).order_by('username')
    other_task_objects = Task.objects.filter(project=specified_project_object).order_by('-id')

    return render(request, 'main/task_create_or_update.html', {
        'specified_project_object': specified_project_object,
        'priority_choice_tuple_list': PRIORITY_CHOICE_TUPLE_LIST,
        'user_objects': user_objects,
        'request_user': request.user,
        'status_choice_tuple_list': STATUS_CHOICE_TUPLE_LIST,
        'other_tasks': other_task_objects,
    })


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = 'queryset_list'

    def get_queryset(self):
        queryset = Task.objects.filter(Q(user=self.request.user)|Q(user=None)).order_by('-id')
        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    context_object_name = 'task'


def task_update(request, pk):
    task_object = Task.objects.get(pk=pk)

    task_object.pre_tasks = []
    taskposition_objects = TaskPosition.objects.filter(post=task_object)
    for taskposition_object in taskposition_objects:
        task_object.pre_tasks.append(taskposition_object.pre)

    project_objects = Project.objects.order_by('name')

    user_objects = User.objects.order_by('username')

    other_task_objects = Task.objects.filter(project=task_object.project).order_by('-id')
    
    return render(request, 'main/task_create_or_update.html', {
        'task': task_object,
        'project_objects': project_objects,
        'priority_choice_tuple_list': PRIORITY_CHOICE_TUPLE_LIST,
        'user_objects': user_objects,
        'request_user': request.user,
        'status_choice_tuple_list': STATUS_CHOICE_TUPLE_LIST,
        'other_tasks': other_task_objects,
    })


def task_create_or_update_submit(request):
    id = request.POST.get('id').strip()
    project = request.POST.get('project').strip()
    title = request.POST.get('title').strip()
    description = request.POST.get('description').strip()
    reference = request.POST.get('reference').strip()
    milestone = request.POST.get('milestone')
    priority = request.POST.get('priority').strip()
    cost = request.POST.get('cost').strip()
    start = request.POST.get('start').strip()
    deadline = request.POST.get('deadline').strip()
    user = request.POST.get('user').strip()
    status = request.POST.get('status').strip()
    
    if id == '':
        id = 0
    else:
        id = int(id)

    project_object = None
    if project != '':
        project_object = Project.objects.get(pk=int(project))

    title = 'Untitled' if title == '' else title
    
    description = None if description == '' else description
    
    reference = None if reference == '' else reference

    milestone = True if milestone == 'on' else False

    priority = 0 if priority == '' else int(priority)

    cost = 0 if cost == '' else int(cost)
    if milestone:
        cost = 0

    start_datetime = None
    if start != '' and start != '--------------':
        m0 = re.match('([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]+)/%d' % RESOLUTION, start)
        if m0:
            start_datetime = datetime(
                year=int(m0.group(1)),
                month=int(m0.group(2)),
                day=int(m0.group(3)),
                hour=(24 // RESOLUTION * int(m0.group(4))),
                tzinfo=LOCAL_TIME_ZONE_INFO,
            )
        else:
            m1 = re.match('([0-9]{4})-([0-9]{2})-([0-9]{2})', start)
            if m1:
                start_datetime = convert_timestr_yyyy_mm_dd_to_datetime(start)

    deadline_datetime = None
    if deadline != '' and start != '--------------':
        m0 = re.match('([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]+)/%d' % RESOLUTION, deadline)
        if m0:
            deadline_datetime = datetime(
                year=int(m0.group(1)),
                month=int(m0.group(2)),
                day=int(m0.group(3)),
                hour=(24 // RESOLUTION * int(m0.group(4))),
                tzinfo=LOCAL_TIME_ZONE_INFO,
            )
        else:
            m1 = re.match('([0-9]{4})-([0-9]{2})-([0-9]{2})', deadline)
            if m1:
                deadline_datetime = convert_timestr_yyyy_mm_dd_to_datetime(deadline)

    user_object = None if user == '' else User.objects.get(pk=int(user))

    status = 0 if status == '' else int(status)

    try:
        task_object = Task.objects.get(pk=id)
    except Task.DoesNotExist:
        task_object = Task(
            project = project_object,
            title = title,
            description = description,
            reference = reference,
            milestone = milestone,
            priority = priority,
            cost = cost,
            start = start_datetime,
            deadline = deadline_datetime,
            user = user_object,
            status = status,
        )
    else:
        task_object.project = project_object
        task_object.title = title
        task_object.description = description
        task_object.reference = reference
        task_object.milestone = milestone
        task_object.priority = priority
        task_object.cost = cost
        task_object.start = start_datetime
        task_object.deadline = deadline_datetime
        task_object.user = user_object
        task_object.status = status

    task_object.save()

    i = 1
    while request.POST.get('pre_task_%d' % i):
        pre_task = request.POST.get('pre_task_%d' % i).strip()
        first_space_index = pre_task.find(' ')
        pre_task_id = int(pre_task[1:first_space_index])
        pre_task_object = Task.objects.get(pk=pre_task_id)
        try:
            taskposition_object = TaskPosition.objects.get(pre=pre_task_object, post=task_object)
        except TaskPosition.DoesNotExist:
            taskposition_object = TaskPosition(
                pre = pre_task_object,
                post = task_object,
            )
            taskposition_object.save()
        i = i + 1

    if project_object is None:
        refresh_serie_objects(request.user)
    else:
        group_object = project_object.group
        user_objects = group_object.user_set.order_by('username')
        for user in user_objects:
            refresh_serie_objects(user)

    return HttpResponseRedirect(reverse('main:task_detail', args=(task_object.pk,)))


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:task_list')


class TaskPositionListView(LoginRequiredMixin, generic.ListView):
    model = TaskPosition
    context_object_name = 'queryset_list'

    def get_queryset(self):
        pks = []
        groups = list(self.request.user.groups.all().order_by('name'))
        for taskposition_object in TaskPosition.objects.all().order_by('-id'):
            if taskposition_object.pre.project.group in groups \
                    or taskposition_object.post.project.group in groups:
                pks.append(taskposition_object.pk)
        return TaskPosition.objects.filter(pk__in=pks)


class TaskPositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskPosition
    context_object_name = 'taskposition'


class TaskPositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskPosition
    fields = ['pre', 'post']
    template_name = 'main/create.html'


class TaskPositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskPosition
    fields = ['pre', 'post']
    template_name = 'main/update.html'


class TaskPositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskPosition
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:taskposition_list')


class CalendarListView(LoginRequiredMixin, generic.ListView):
    model = Calendar
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Calendar.objects.order_by('date')


class CalendarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Calendar
    context_object_name = 'calendar'


class CalendarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Calendar
    fields = ['date', 'is_holiday']
    template_name = 'main/create.html'


class CalendarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Calendar
    fields = ['date', 'is_holiday']
    template_name = 'main/update.html'


class CalendarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Calendar
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:calendar_list')


class AlgorithmListView(LoginRequiredMixin, generic.ListView):
    model = Algorithm
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Algorithm.objects.filter(user=self.request.user)


class AlgorithmDetailView(LoginRequiredMixin, generic.DetailView):
    model = Algorithm
    context_object_name = 'algorithm'


class AlgorithmCreateView(LoginRequiredMixin, generic.CreateView):
    model = Algorithm
    fields = ['user', 'code', 'accepted']
    template_name = 'main/create.html'


class AlgorithmUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Algorithm
    fields = ['user', 'code', 'accepted']
    template_name = 'main/update.html'


class AlgorithmDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Algorithm
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:algorithm_list')


class SerieListView(LoginRequiredMixin, generic.ListView):
    model = Serie
    context_object_name = 'queryset_list'

    def get_queryset(self):
        return Serie.objects.all()


class SerieDetailView(LoginRequiredMixin, generic.DetailView):
    model = Serie
    context_object_name = 'serie'


class SerieCreateView(LoginRequiredMixin, generic.CreateView):
    model = Serie
    fields = ['task', 'start', 'end']
    template_name = 'main/create.html'


class SerieUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Serie
    fields = ['task', 'start', 'end']
    template_name = 'main/update.html'


class SerieDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Serie
    template_name = 'main/confirm_delete.html'
    success_url = reverse_lazy('main:serie_list')
