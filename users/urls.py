from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),
    path('change-password/', views.change_password, name='change_password'),
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('password-reset-sent/<str:reset_id>/', views.password_reset_sent, name='password_reset_sent'),
    path('reset-password/<str:reset_id>/', views.reset_password, name='reset_password'),
]