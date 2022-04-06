from django.urls import path

from . import views


app_name = 'main'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.login, name='login'),
    path('login/submit', views.login_submit, name='login_submit'),
    
    path('user/list', views.UserListView.as_view(), name='user_list'),
    path('user/create', views.UserCreateView.as_view(), name='user_create'),
    path('user/<int:pk>', views.UserDetailView.as_view(), name='user_detail'),
    path('user/<int:pk>/update', views.UserUpdateView.as_view(), name='user_update'),
    path('user/<int:pk>/delete', views.UserDeleteView.as_view(), name='user_delete'),

    path('project/list', views.ProjectListView.as_view(), name='project_list'),
    path('project/create', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/update', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete', views.ProjectDeleteView.as_view(), name='project_delete'),

    path('task/list', views.TaskListView.as_view(), name='task_list'),
    path('task/create', views.task_create, name='task_create'),
    path('task/create/or/update/submit', views.task_create_or_update_submit, name='task_create_or_update_submit'),
    path('task/<int:pk>', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/update', views.task_update, name='task_update'),
    path('task/<int:pk>/delete', views.TaskDeleteView.as_view(), name='task_delete'),

    path('taskposition/list', views.TaskPositionListView.as_view(), name='taskposition_list'),
    path('taskposition/create', views.TaskPositionCreateView.as_view(), name='taskposition_create'),
    path('taskposition/<int:pk>', views.TaskPositionDetailView.as_view(), name='taskposition_detail'),
    path('taskposition/<int:pk>/update', views.TaskPositionUpdateView.as_view(), name='taskposition_update'),
    path('taskposition/<int:pk>/delete', views.TaskPositionDeleteView.as_view(), name='taskposition_delete'),

    path('calendar/list', views.CalendarListView.as_view(), name='calendar_list'),
    path('calendar/create', views.CalendarCreateView.as_view(), name='calendar_create'),
    path('calendar/<str:pk>', views.CalendarDetailView.as_view(), name='calendar_detail'),
    path('calendar/<str:pk>/update', views.CalendarUpdateView.as_view(), name='calendar_update'),
    path('calendar/<str:pk>/delete', views.CalendarDeleteView.as_view(), name='calendar_delete'),

    path('serie/list', views.SerieListView.as_view(), name='serie_list'),
    path('serie/create', views.SerieCreateView.as_view(), name='serie_create'),
    path('serie/<str:pk>', views.SerieDetailView.as_view(), name='serie_detail'),
    path('serie/<str:pk>/update', views.SerieUpdateView.as_view(), name='serie_update'),
    path('serie/<str:pk>/delete', views.SerieDeleteView.as_view(), name='serie_delete'),
]