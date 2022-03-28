from django.db import models
from django.urls import reverse

import time


# Create your models here.


PRIORITY_CHOICE_TUPLE = ((0, '☆☆☆'), (1, '★☆☆'), (2, '★★☆'), (3, '★★★'))
PRIORITY_CHOICE_LIST = ['☆☆☆', '★☆☆', '★★☆', '★★★']


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, default=None, blank=False, null=False)
    description = models.TextField(max_length=65535, default=None, blank=False, null=True)
    reference = models.CharField(max_length=255, default=None, blank=True, null=True)
    priority = models.IntegerField(default=0, blank=False, null=False, choices=PRIORITY_CHOICE_TUPLE)
    cost = models.IntegerField(default=0, blank=False, null=False)
    deadline = models.DateField(default=None, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('main:task_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return self.title


class Calendar(models.Model):
    date = models.DateField(primary_key=True)
    is_holiday = models.BooleanField(max_length=255, default=False, blank=False, null=False)

    def get_absolute_url(self):
        return reverse('main:calendar_detail', kwargs={'pk':self.pk})

    def date_yyyy_mm_dd(self):
        return str(self.date)

    def __str__(self):
        return '%s %s' % (self.date, self.is_holiday)
