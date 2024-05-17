from django.urls import path
from accounts import views
from accounts.views import RecruiterListView, ClientListView, TaskListView

"""
Imports explanation:

1. from django.urls import path
   - path: Funkcja Django do definiowania tras URL w aplikacji. Używana do mapowania widoków na konkretne ścieżki URL.

2. from accounts import views
   - views: Moduł zawierający wszystkie widoki w aplikacji accounts. Importujemy go, aby uzyskać dostęp do funkcji widoków.

3. from accounts.views import RecruiterListView, ClientListView, TaskListView
   - RecruiterListView: Klasa widoku listy rekruterów.
   - ClientListView: Klasa widoku listy klientów.
   - TaskListView: Klasa widoku listy zadań.
"""

app_name = 'accounts'
"""
Ustawia nazwę przestrzeni nazw dla tej aplikacji.
Umożliwia organizowanie URL w różnych aplikacjach.
"""

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create_profile/', views.create_profile, name='create_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_detail_view, name='profile_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:task_id>/edit/', views.task_update_view, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),
    path('recruiters/', RecruiterListView.as_view(), name='recruiters'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('verify/<str:token>/', views.verify_email_view, name='verify_email'),
    path('verified/', views.verified_view, name='verified'),
    path('registration_complete/', views.registration_complete_view, name='registration_complete'),
    path('change-password/', views.change_password, name='change_password'),
]
