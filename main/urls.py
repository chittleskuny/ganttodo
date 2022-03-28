from django.urls import path

from . import views


app_name = 'main'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('task/list', views.TaskListView.as_view(), name='task_list'),
    path('task/create', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/update', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete', views.TaskDeleteView.as_view(), name='task_delete'),

    path('calendar/list', views.CalendarListView.as_view(), name='calendar_list'),
    path('calendar/create', views.CalendarCreateView.as_view(), name='calendar_create'),
    path('calendar/<str:pk>', views.CalendarDetailView.as_view(), name='calendar_detail'),
    path('calendar/<str:pk>/update', views.CalendarUpdateView.as_view(), name='calendar_update'),
    path('calendar/<str:pk>/delete', views.CalendarDeleteView.as_view(), name='calendar_delete'),
]