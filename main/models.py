from django.contrib.auth.models import User, Group
from django.db import models
from django.urls import reverse

from .clocks import *


# Create your models here.


PRIORITY_CHOICE_INT_LIST = [0, 1, 2, 3]
PRIORITY_CHOICE_STR_LIST = ['☆☆☆', '★☆☆', '★★☆', '★★★']
PRIORITY_CHOICE_TUPLE_LIST = ((0, '☆☆☆'), (1, '★☆☆'), (2, '★★☆'), (3, '★★★'))

STATUS_CHOICE_INT_LIST = [0, 1, 2, 3]
STATUS_CHOICE_STR_LIST = ['Todo', 'Doing', 'Done', 'Aborted']
STATUS_CHOICE_TUPLE_LIST = ((0, 'Todo'), (1, 'Doing'), (2, 'Done'), (3, 'Aborted'))


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, default=None, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default=None, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:project_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, default=None, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default=None, blank=False, null=False)
    description = models.TextField(max_length=65535, default=None, blank=True, null=True)
    reference = models.CharField(max_length=255, default=None, blank=True, null=True)
    milestone = models.BooleanField(default=False, blank=False, null=False)
    priority = models.IntegerField(default=0, blank=False, null=False, choices=PRIORITY_CHOICE_TUPLE_LIST)
    cost = models.IntegerField(default=0, blank=False, null=False)
    start = models.DateTimeField(default=None, blank=True, null=True)
    deadline = models.DateTimeField(default=None, blank=True, null=True)
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, blank=False, null=False, choices=STATUS_CHOICE_TUPLE_LIST)

    def get_absolute_url(self):
        return reverse('main:task_detail', kwargs={'pk': self.pk})

    @property
    def priority_str(self):
        return PRIORITY_CHOICE_STR_LIST[self.priority]

    @property
    def cost_timedelta(self):
        return UNIT * self.cost

    @property
    def start_timestr_yyyy_mm_dd(self):
        return '--------------' if self.start is None else convert_datetime_to_timestr_yyyy_mm_dd_fraction(self.start)

    @property
    def end_timestr_yyyy_mm_dd(self):
        end_timestr_yyyy_mm_dd = '--------------'
        if self.status in (STATUS_CHOICE_STR_LIST.index('Done'), STATUS_CHOICE_STR_LIST.index('Aborted')):
            end_datetime = self.start + UNIT * self.cost
            end_timestr_yyyy_mm_dd = convert_datetime_to_timestr_yyyy_mm_dd_fraction(end_datetime)
        return end_timestr_yyyy_mm_dd

    @property
    def deadline_timestr_yyyy_mm_dd(self):
        return '--------------' if self.deadline is None else convert_datetime_to_timestr_yyyy_mm_dd_fraction(self.deadline)

    @property
    def start_end(self):
        return '[%s, %s]' % (self.start_timestr_yyyy_mm_dd, self.end_timestr_yyyy_mm_dd)
        
    @property
    def status_str(self):
        return STATUS_CHOICE_STR_LIST[self.status]

    def __str__(self):
        return '#%d %s' % (self.id, self.title)


class TaskPosition(models.Model):
    id = models.AutoField(primary_key=True)
    pre = models.ForeignKey(Task, related_name='pre_task', default=None, blank=False, null=False, on_delete=models.CASCADE)
    post = models.ForeignKey(Task, related_name='post_task', default=None, blank=False, null=False, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('main:taskposition_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s -> %s' % (self.pre, self.post)


class Calendar(models.Model):
    date = models.DateField(primary_key=True)
    is_holiday = models.BooleanField(default=False, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:calendar_detail', kwargs={'pk': self.pk})

    @property
    def date_timestr_yyyy_mm_dd(self):
        return str(self.date)

    def __str__(self):
        return '%s %s' % (self.date, self.is_holiday)


class Algorithm(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, default=None, blank=None, null=None, on_delete=models.CASCADE)
    code = models.TextField(max_length=65535, default=None, blank=False, null=True)
    accepted = models.BooleanField(default=False, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:algorithm_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '[%s] %s\'s algorithm' % (self.accepted, self.user)


class Serie(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, default=None, blank=None, null=None, on_delete=models.CASCADE)
    start = models.DateTimeField(default=0, blank=False, null=False)
    end = models.DateTimeField(default=0, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:serie_detail', kwargs={'pk': self.pk})

    @property
    def start_timestr_yyyy_mm_dd_fraction(self):
        return convert_datetime_to_timestr_yyyy_mm_dd_fraction(self.start)

    @property
    def end_timestr_yyyy_mm_dd_fraction(self):
        return convert_datetime_to_timestr_yyyy_mm_dd_fraction(self.end, ZERO_LEFT)

    def __str__(self):
        return '[%s, %s] #%d %s => %s' % (
            self.start_timestr_yyyy_mm_dd_fraction,
            self.end_timestr_yyyy_mm_dd_fraction,
            self.task.id,
            self.task.title,
            self.task.user,
        )
