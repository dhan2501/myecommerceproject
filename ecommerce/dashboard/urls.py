from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),  # <-- this line
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    path('users/', views.user_list, name='dashboard_users'),
    path('reports/', views.reports, name='dashboard_reports'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    path('users/', views.user_list, name='user_list'),
    

    
]