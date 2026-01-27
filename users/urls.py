from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='Signup'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]
