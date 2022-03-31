from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.


PRIORITY_CHOICE_TUPLE = ((0, '☆☆☆'), (1, '★☆☆'), (2, '★★☆'), (3, '★★★'))
PRIORITY_CHOICE_LIST = ['☆☆☆', '★☆☆', '★★☆', '★★★']

STATUS_CHOICE_TUPLE = ((0, 'Todo'), (1, 'Doing'), (2, 'Done'), (4, 'Aborted'))
STATUS_CHOICE_LIST = ['Todo', 'Doing', 'Done', 'Aborted']


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default=None, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:project_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return self.name


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, default=None, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default=None, blank=False, null=False)
    description = models.TextField(max_length=65535, default=None, blank=False, null=True)
    reference = models.CharField(max_length=255, default=None, blank=True, null=True)
    milestone = models.BooleanField(default=False, blank=False, null=False)
    priority = models.IntegerField(default=0, blank=False, null=False, choices=PRIORITY_CHOICE_TUPLE)
    cost = models.IntegerField(default=0, blank=False, null=False)
    start = models.DateField(default=None, blank=True, null=True)
    deadline = models.DateField(default=None, blank=True, null=True)
    assignee = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, blank=False, null=False, choices=STATUS_CHOICE_TUPLE)

    def get_absolute_url(self):
        return reverse('main:task_detail', kwargs={'pk':self.pk})

    def start_yyyy_mm_dd(self):
        return '' if self.start is None else str(self.start)

    def deadline_yyyy_mm_dd(self):
        return '' if self.deadline is None else str(self.deadline)

    def __str__(self):
        return '#%d %s' % (self.id, self.title)


class TaskPosition(models.Model):
    id = models.AutoField(primary_key=True)
    pre = models.ForeignKey(Task, related_name='pre_task', default=None, blank=False, null=False, on_delete=models.CASCADE)
    post = models.ForeignKey(Task, related_name='post_task', default=None, blank=False, null=False, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('main:taskposition_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return '%s -> %s' % (self.pre, self.post)


class Calendar(models.Model):
    date = models.DateField(primary_key=True)
    is_holiday = models.BooleanField(default=False, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:calendar_detail', kwargs={'pk':self.pk})

    def date_yyyy_mm_dd(self):
        return str(self.date)

    def __str__(self):
        return '%s %s' % (self.date, self.is_holiday)
