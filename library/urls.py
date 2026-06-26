from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('create/', views.document_create, name='document_create'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
]
