# projects/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Q 
from .models import Project
from properties.models import Property # Needed for project_details if included
# Import related models for dropdowns
from utility.models import City, Locality # Locality and City imported
# Import related models for dropdowns
from utility.models import City, Locality # Locality and City imported
from .models import (
    Project, Configuration, Gallery, RERA_Info, BookingOffer, 
    Overview, USP, Amenities as ProjectAmenitiesModel # Project details models
) 


# --- 1. All Projects Listing Page (Optimized Index) ---
def index(request):
    # Start with all active projects
    queryset_list = Project.objects.filter(active=True).order_by('project_name')

    # --- Filtering Logic ---
    
    # 1. City Filter (Standard Foreign Key)
    if 'city_id' in request.GET and request.GET['city_id']:
        city_id = request.GET['city_id']
        queryset_list = queryset_list.filter(city_id=city_id)

    # 2. Locality Filter (MPTT Descendants Implementation)
    if 'locality_id' in request.GET and request.GET['locality_id']:
        locality_id = request.GET['locality_id']
        try:
            # Get the selected Locality node (e.g., Phase 1)
            selected_locality = Locality.objects.get(pk=locality_id)
            
            # Fetch all descendants (sub-localities) including the node itself
            descendant_localities = selected_locality.get_descendants(include_self=True)
            
            # Filter projects whose locality FK is within the fetched MPTT tree
            queryset_list = queryset_list.filter(locality__in=descendant_localities)
            
        except Locality.DoesNotExist:
            pass # Ignore if invalid ID is passed


    # 3. Status Filter
    if 'status' in request.GET and request.GET['status']:
        status = request.GET['status']
        queryset_list = queryset_list.filter(construction_status__iexact=status)

    # 4. Keyword Search (Project Name or Developer Name)
    if 'keywords' in request.GET and request.GET['keywords']:
        keywords = request.GET['keywords']
        queryset_list = queryset_list.filter(
            Q(project_name__icontains=keywords) | 
            Q(developer__name__icontains=keywords)
        )
        
    # --- Context ---
    
    available_cities = City.objects.all().order_by('name')
    # Fetch all *top-level* Localities for the main dropdown (or all of them if preferred)
    available_localities = Locality.objects.filter(parent__isnull=True).order_by('name')
    construction_statuses = Project.Construction_Status
    
    context = {
        'projects': queryset_list,
        'available_cities': available_cities,
        'available_localities': available_localities,
        'construction_statuses': construction_statuses,
        'values': request.GET, # Passes submitted values back to the form
    }
    
    return render(request, 'projects/projects.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Project

# 🏠 Residential Projects
def residential_projects(request):
    query = request.GET.get('q', '')
    projects = Project.objects.filter(
        propert_type__parent__name__iexact='Residential',
        active=True
    ).select_related('city', 'locality', 'propert_type')

    if query:
        projects = projects.filter(project_name__icontains=query)

    context = {
        'projects': projects,
        'page_title': 'Residential Projects',
        'breadcrumb': 'Residential',
    }
    return render(request, 'projects/residential_list.html', context)


# 🏢 Commercial Projects
def commercial_projects(request):
    query = request.GET.get('q', '')
    projects = Project.objects.filter(
        propert_type__parent__name__iexact='Commercial',
        active=True
    ).select_related('city', 'locality', 'propert_type')

    if query:
        projects = projects.filter(project_name__icontains=query)

    context = {
        'projects': projects,
        'page_title': 'Commercial Projects',
        'breadcrumb': 'Commercial',
    }
    return render(request, 'projects/commercial_list.html', context)


# 🔍 Project Details
def project_details(request, id, slug):
    project = get_object_or_404(Project, id=id, slug=slug)
    context = {
        'project': project,
        'title': project.project_name
    }
    return render(request, 'projects/project_details.html', context)

# --- 2. Project Detail Page (From Step 50) ---
def project_details(request, id, slug):

    """
    Renders the detail page for a single project, fetching all related content 
    using the optimized related_name access.
    """
    # Fetch the main project object by ID and slug
    project = get_object_or_404(Project, slug=slug, active=True)

    # 1. Fetch related properties (Fixing the AttributeError source)
    # The related_name 'unit_listings' is used to query individual properties belonging to this project.
    project_properties = project.unit_listings.filter(is_published=True).order_by('-list_date')
    
    # 2. Compile Context (Using related_name access)
    context = {
        'project': project,
        'properties': project_properties, # The list of associated properties
        
        # Optimized access for related models:
        'configurations': project.configurations.all().order_by('bhk_type'),
        'galleries': project.gallery.all(),
        'rera_info': project.rera.first(), 
        'amenities': project.amenities.all(),
        'overview': project.overviews.first(),
        'usps': project.usps.all(),
        'booking_offers': project.BookingOffer.all(),
        
        # Note: All related models (WelcomeTo, WebSlider, etc.) are implicitly accessed 
        # via project.related_name.all() or project.related_name.first()
    }
    return render(request, 'projects/project_detail.html', context)