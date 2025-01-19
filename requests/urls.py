from django.urls import path
from . import views

urlpatterns = [
    path('create_request/', views.create_request, name='create_request'),
    path('delete_request/', views.delete_request, name='delete_request'),
    path('get_requests/', views.get_requests, name='get_requests'),
    path('admin/chnage_status/', views.chnage_status_admin, name='chnage_status_admin'),
    path('admin/delete_request/', views.delete_request_admin, name='delete_request_admin'),
    path('admin/get_requests/', views.get_requests_admin, name='get_requests_admin'),
    # path('login/', views.user_login, name='login'),
]