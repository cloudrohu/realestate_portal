# projects/urls.py (Corrected)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='projects'), 
    # Change 'project_details' to 'project_detail' (assuming your view uses the singular name)
    path('<int:id>/<slug:slug>/', views.project_details, name='project_details'), 
]