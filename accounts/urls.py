# В файле urls.py для приложения accounts
from django.urls import path

from accounts import views
from accounts.views import register_user, create_profile, login_view, logout_view, dashboard_view, RecruiterListView, \
    ClientListView, TaskListView

app_name = 'accounts'

urlpatterns = [
    path('register/', register_user, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create_profile/', create_profile, name='create_profile'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', views.profile_detail_view, name='profile_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:task_id>/edit/', views.task_update_view, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),
    path('recruiters/', RecruiterListView.as_view(), name='recruiters'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
]
