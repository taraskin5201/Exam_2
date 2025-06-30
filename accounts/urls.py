from django.urls import path
from . import views
from django.contrib.auth import views as auth_views




urlpatterns = [

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('delete/', views.delete_account, name='delete_account'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/password_change_done/'  # <- обов’язково!
    ), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    path('works/', views.work_list, name='work_list'),
    path('works/new/', views.create_work, name='create_work'),
    path('works/<int:pk>/', views.work_detail, name='work_detail'),
    path('work/<int:pk>/edit/', views.edit_work, name='edit_work'),
    path('work/<int:work_id>/delete/', views.delete_work, name='delete_work'),
    path('works/<int:pk>/', views.work_detail, name='work_detail'),


]
