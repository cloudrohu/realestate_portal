# home/views.py (FINAL CLEANED VERSION)

from django.shortcuts import render
from django.http import HttpResponse 
from properties.models import Property 
from utility.models import Locality,PropertyType
from .models import (
    Setting, Slider, Testimonial, About_Page, 
    Contact_Page, FAQ, Our_Team
)

# NOTE: The manual function get_global_context() has been removed 
#       because the utility.context_processors handles this globally.

# ==========================================================
# 🌐 MAIN VIEWS
# ==========================================================

def index(request):
    """
    Renders the main landing page, fetching featured properties and site content.
    """
    settings_obj = Setting.objects.first()

    # 1. Fetch Featured Properties 
    latest_properties = Property.objects.order_by('-list_date').filter(is_published=True)[:4]
    
    # 2. Fetch Home Page Content 
    sliders = Slider.objects.filter(setting=settings_obj, is_active=True).order_by('order') if settings_obj else None
    testimonials = Testimonial.objects.filter(setting=settings_obj).order_by('?') if settings_obj else None
    
    # 3. MPTT Data for Search Bar (CRITICAL for Homepage Search)
    top_level_types = PropertyType.objects.filter(parent__isnull=True).order_by('name')
    top_level_localities = Locality.objects.filter(parent__isnull=True).order_by('name')

    context = {
        'properties': latest_properties,
        'sliders': sliders,
        'testimonials': testimonials,
        # Injected data for the search bar template
        'top_level_types': top_level_types,
        'top_level_localities': top_level_localities,
    }
    
    def global_settings_processor(request):
        """
        Context processor to make site-wide settings available in all templates.
        Crashes if Setting model or its dependency (like ImageCompressionMixin) has an issue.
        """
        try:
            # Fetch the main site settings object safely
            settings = Setting.objects.first()
        except Exception as e:
            # If the database is empty or an import fails, settings will be None.
            # Print the error for local debugging, but prevent crash.
            print(f"CRITICAL CONTEXT ERROR: {e}") 
            settings = None

        return {
            'site_settings': settings,
        }

    return render(request, 'home/index.html', context)


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
        'contact_content': contact_content,
    }
    return render(request, 'home/contact.html', context)


def faq_view(request):
    """Renders the FAQ page."""
    settings_obj = Setting.objects.first()
    
    # Fetch all FAQs
    faqs = FAQ.objects.filter(setting=settings_obj).order_by('id') if settings_obj else None
    
    context = {
        'faqs': faqs
    }
    return render(request, 'home/faq.html', context)