from django.urls import path

from . import views


app_name = 'main'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('accounts/profile/', views.accounts_profile, name='accounts_profile'),
    path('accounts/login/', views.accounts_login, name='accounts_login'),
    path('accounts/login/submit', views.accounts_login_submit, name='accounts_login_submit'),
    path('accounts/logout/submit', views.accounts_logout_submit, name='accounts_logout_submit'),
    path('accounts/refresh/submit', views.accounts_refresh_submit, name='accounts_refresh_submit'),

    path('group/list/', views.group_list, name='group_list'),
    path('group/<int:pk>/', views.group_detail, name='group_detail'),
    path('group/<int:pk>/project/create/', views.group_project_create, name='group_project_create'),

    path('project/list/', views.ProjectListView.as_view(), name='project_list'),
    path('project/create/or/update/submit', views.project_create_or_update_submit, name='project_create_or_update_submit'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('project/<int:pk>/task/list/', views.project_task_list, name='project_task_list'),
    path('project/<int:pk>/task/create/', views.project_task_create, name='project_task_create'),

    path('task/list/', views.TaskListView.as_view(), name='task_list'),
    path('task/create/or/update/submit', views.task_create_or_update_submit, name='task_create_or_update_submit'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/update/', views.task_update, name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    path('taskposition/list/', views.TaskPositionListView.as_view(), name='taskposition_list'),
    path('taskposition/create/', views.TaskPositionCreateView.as_view(), name='taskposition_create'),
    path('taskposition/<int:pk>/', views.TaskPositionDetailView.as_view(), name='taskposition_detail'),
    path('taskposition/<int:pk>/update/', views.TaskPositionUpdateView.as_view(), name='taskposition_update'),
    path('taskposition/<int:pk>/delete/', views.TaskPositionDeleteView.as_view(), name='taskposition_delete'),

    path('calendar/list/', views.CalendarListView.as_view(), name='calendar_list'),
    path('calendar/create/', views.CalendarCreateView.as_view(), name='calendar_create'),
    path('calendar/<str:pk>/', views.CalendarDetailView.as_view(), name='calendar_detail'),
    path('calendar/<str:pk>/update/', views.CalendarUpdateView.as_view(), name='calendar_update'),
    path('calendar/<str:pk>/delete/', views.CalendarDeleteView.as_view(), name='calendar_delete'),

    path('algorithm/list/', views.AlgorithmListView.as_view(), name='algorithm_list'),
    path('algorithm/create/', views.AlgorithmCreateView.as_view(), name='algorithm_create'),
    path('algorithm/<str:pk>/', views.AlgorithmDetailView.as_view(), name='algorithm_detail'),
    path('algorithm/<str:pk>/update/', views.AlgorithmUpdateView.as_view(), name='algorithm_update'),
    path('algorithm/<str:pk>/delete/', views.AlgorithmDeleteView.as_view(), name='algorithm_delete'),

    path('serie/list/', views.SerieListView.as_view(), name='serie_list'),
    path('serie/create/', views.SerieCreateView.as_view(), name='serie_create'),
    path('serie/<str:pk>/', views.SerieDetailView.as_view(), name='serie_detail'),
    path('serie/<str:pk>/update/', views.SerieUpdateView.as_view(), name='serie_update'),
    path('serie/<str:pk>/delete/', views.SerieDeleteView.as_view(), name='serie_delete'),
]