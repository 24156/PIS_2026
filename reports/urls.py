from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('statistiques/', views.statistiques, name='statistiques'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
