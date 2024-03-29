from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    path('password_reset_form/', PasswordResetView.as_view(),
         name='password_reset_form'),
]
