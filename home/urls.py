from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('robots.txt', views.robots_txt, name='robots_txt'),

    path('about/', views.about_page_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),

    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('terms-cookies/', views.cookies, name='cookies'),

    path("home-contact/", views.submit_home_contact, name="home_contact"),
]
