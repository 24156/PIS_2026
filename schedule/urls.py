from django.urls import path

from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.emploi_list, name='emploi_list'),
    path('create/', views.emploi_create, name='emploi_create'),
    path('<int:pk>/edit/', views.emploi_edit, name='emploi_edit'),
    path('<int:pk>/delete/', views.emploi_delete, name='emploi_delete'),
]
