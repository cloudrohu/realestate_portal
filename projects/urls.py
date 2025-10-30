# projects/urls.py (Corrected)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='projects'), 

    path('residential/', views.residential_projects, name='residential_projects'),
    path('commercial/', views.commercial_projects, name='commercial_projects'),
    # Change 'project_details' to 'project_detail' (assuming your view uses the singular name)
    path('<int:id>/<slug:slug>/', views.project_details, name='project_details'), 
    path('submit-enquiry/<int:id>/', views.submit_enquiry, name='submit_enquiry'),
    path('thank-you/', views.thank_you, name='thank_you'),

]