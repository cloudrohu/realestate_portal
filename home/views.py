
from django.shortcuts import render
from django.http import HttpResponse 
from properties.models import Property 
from utility.models import Locality,PropertyType
from .models import (
    Setting, Slider, Testimonial, About_Page, 
    Contact_Page, FAQ, Our_Team
)
from utility.models import City
# NOTE: The manual function get_global_context() has been removed 
#       because the utility.context_processors handles this globally.

from django.shortcuts import render
from projects.models import Project  # import your Project model

def index(request):
    settings_obj = Setting.objects.first()
    cities = City.objects.filter(level_type="CITY").order_by("name")

    project_featured = (
        Project.objects.filter(featured_property=True, active=True)
        .select_related("city", "locality", "developer", "propert_type")
        .prefetch_related("configurations")[:6]
    )

    current_city = None
    if project_featured.exists() and project_featured[0].city:
        current_city = project_featured[0].city.name

    context = {
        "settings_obj": settings_obj,
        "project_featured": project_featured,
        "cities": cities,  # 👈 dynamic data from City model
        "current_city": current_city or "Mumbai",
    }

    return render(request, "home/index.html", context)




def robots_txt(request):
    """
    Serves the robots.txt file content for SEO.
    """
    robots_content = """
User-agent: *
Disallow: /admin/
Disallow: /accounts/
Allow: /

Sitemap: http://127.0.0.1:8000/sitemap.xml 
    """
    return HttpResponse(robots_content.strip(), content_type="text/plain")


def about_view(request):
    """Renders the About Us page."""
    settings_obj = Setting.objects.first()
    
    # Fetch About Content and Team members
    about_content = About_Page.objects.filter(setting=settings_obj).first() if settings_obj else None
    team_members = Our_Team.objects.filter(setting=settings_obj).order_by('name') if settings_obj else None
    
    context = {
        "settings_obj": settings_obj,

        'about_content': about_content,
        'team_members': team_members
    }
    return render(request, 'home/about.html', context)


def contact_view(request):
    """Renders the Contact Page with site contact details."""
    settings_obj = Setting.objects.first()
    
    # Fetch Contact Content
    contact_content = Contact_Page.objects.filter(setting=settings_obj).first() if settings_obj else None

    context = {
        "settings_obj": settings_obj,

        'contact_content': contact_content,
    }
    return render(request, 'home/contact.html', context)


def faq_view(request):
    """Renders the FAQ page."""
    settings_obj = Setting.objects.first()
    
    # Fetch all FAQs
    faqs = FAQ.objects.filter(setting=settings_obj).order_by('id') if settings_obj else None
    
    context = {
        "settings_obj": settings_obj,

        'faqs': faqs
    }
    return render(request, 'home/faq.html', context)