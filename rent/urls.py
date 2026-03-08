from django.urls import path
from . import views

urlpatterns = [
   path('', views.rent_list, name='rent_list'),
   path('<slug:slug>-rental-details/', views.rental_detail, name='rental_detail'),
   path("rent/thank-you/", views.rent_thank_you, name="rent_thank_you"),
   
]