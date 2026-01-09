# projects/views.py
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q 
from .models import Project
from home.models import Setting
from properties.models import Property # Needed for project_details if included
# Import related models for dropdowns
from utility.models import City, Locality , PropertyType , PossessionIn , ProjectAmenities , Bank , PropertyAmenities
# Import related models for dropdowns
from .models import (
    Project, Configuration, Gallery, RERA_Info, BookingOffer, Overview,
    USP, Amenities, Header, WelcomeTo, Connectivity, WhyInvest,Enquiry,ProjectFAQ
) 

def index(request):
    # Start with all active projects
    queryset_list = Project.objects.filter(active=True).order_by('project_name')

    
    if 'city_id' in request.GET and request.GET['city_id']:
        city_id = request.GET['city_id']
        queryset_list = queryset_list.filter(city_id=city_id)

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


    if 'status' in request.GET and request.GET['status']:
        status = request.GET['status']
        queryset_list = queryset_list.filter(construction_status__iexact=status)

    if 'keywords' in request.GET and request.GET['keywords']:
        keywords = request.GET['keywords']
        queryset_list = queryset_list.filter(
            Q(project_name__icontains=keywords) | 
            Q(developer__name__icontains=keywords)
        )
        
    
    available_cities = City.objects.all().order_by('name')
    amenities = ProjectAmenities.objects.all()
    available_localities = Locality.objects.filter(parent__isnull=True).order_by('name')
    construction_statuses = Project.Construction_Status
    
    context = {
        'projects': queryset_list,
        'available_cities': available_cities,
        "amenities": amenities,
        'construction_statuses': construction_statuses,
        'values': request.GET, # Passes submitted values back to the form
    }
    
    return render(request, 'projects/projects.html', context)

# Helper to get BHK list safely
def get_bhk_choices():
    return [choice[0] for choice in Project.BHK_CHOICES]

def search_projects(request):
    settings_obj = Setting.objects.first()

    # --- 1. Get Params ---
    location = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    amenities = request.GET.get("amenities")
    status = request.GET.get("construction_status")
    bhk = request.GET.get("bhk") 

    # --- 2. Base Query ---
    projects = Project.objects.filter(active=True)

    # --- 3. Filters ---
    if location:
        search_term = location.split(",")[0].strip()
        projects = projects.filter(
            Q(project_name__icontains=search_term) |
            Q(locality__name__icontains=search_term) |
            Q(city__name__icontains=search_term)
        )

    if city:
        projects = projects.filter(city__name__iexact=city)

    # Amenities
    if amenities:
        amenity_list = [a.strip() for a in amenities.split(",") if a]
        if amenity_list:
            projects = projects.filter(amenities__title__in=amenity_list).distinct()

    # Construction Status
    if status:
        status_list = [s.strip() for s in status.split(",") if s]
        if status_list:
            projects = projects.filter(construction_status__in=status_list).distinct()

    # 🔥 BHK FILTER (Fixed)
    selected_bhk_list = []
    if bhk:
        selected_bhk_list = [b.strip() for b in bhk.split(",") if b]
        if selected_bhk_list:
            bhk_query = Q()
            for b in selected_bhk_list:
                # Using icontains because MultiSelectField stores as "1 BHK, 2 BHK"
                bhk_query |= Q(bhk_type__icontains=b)
            projects = projects.filter(bhk_query).distinct()

    # --- 4. Pagination ---
    projects = projects.select_related("city", "locality").prefetch_related("amenities").order_by("-create_at")
    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    # --- 5. Dynamic Choices ---
    status_choices = [choice[0] for choice in Project.Construction_Status]
    
    # 🔥 Get BHK Choices from Model
    bhk_choices = get_bhk_choices()

    context = {
        "projects": projects_page,
        "settings_obj": settings_obj,
        "amenities": ProjectAmenities.objects.all(),
        "construction_status": status_choices,
        
        # 🔥 Dynamic Data for Template
        "bhk_choices": bhk_choices,
        
        # Selected Values
        "selected_amenities": amenities,
        "selected_status": status,
        "selected_bhk": bhk,             # Raw string for Input value
        "selected_bhk_list": selected_bhk_list, # List for strict active check
    }

    return render(request, "projects/residential_list.html", context)

def residential_projects(request):
    settings_obj = Setting.objects.first()

    # --- 1. Get Params ---
    query = request.GET.get("q", "")
    bhk = request.GET.get("bhk")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    amenities = request.GET.get("amenities")
    status = request.GET.get("construction_status")

    # --- 2. Base Query ---
    # Sirf Residential projects lene hain
    projects = (
        Project.objects
        .filter(propert_type__parent__name__iexact="Residential", active=True)
        .select_related("city", "locality", "propert_type")
        .prefetch_related("amenities")
        .annotate(
            min_price=Min("configurations__price_in_rupees"),
            max_price=Max("configurations__price_in_rupees"),
        )
    )

    # --- 3. Filters ---
    if query:
        projects = projects.filter(project_name__icontains=query)

    if min_price:
        projects = projects.filter(max_price__gte=min_price)

    if max_price:
        projects = projects.filter(min_price__lte=max_price)
    
    # Amenities Filter
    if amenities:
        amenity_list = [a.strip() for a in amenities.split(",") if a]
        if amenity_list:
            projects = projects.filter(amenities__title__in=amenity_list).distinct()

    # Construction Status Filter
    if status:
        status_list = [s.strip() for s in status.split(",") if s]
        if status_list:
            projects = projects.filter(construction_status__in=status_list).distinct()

    # 🔥 BHK Filter (MultiSelectField Logic)
    if bhk:
        bhk_list = [b.strip() for b in bhk.split(",") if b]
        if bhk_list:
            bhk_query = Q()
            for b in bhk_list:
                bhk_query |= Q(configurations__bhk_type__icontains=b) | Q(bhk_type__icontains=b)
            projects = projects.filter(bhk_query).distinct()

    # --- 4. Pagination ---
    projects = projects.order_by("-create_at")
    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    # --- 5. Dynamic Choices ---
    status_choices = [choice[0] for choice in Project.Construction_Status]
    bhk_choices = [choice[0] for choice in Project.BHK_CHOICES]

    context = {
        "projects": projects_page,
        "settings_obj": settings_obj,
        "page_title": "Residential Projects",
        "breadcrumb": "Residential",
        
        "amenities": ProjectAmenities.objects.all(),
        "construction_status": status_choices, # Dynamic Status
        "bhk_choices": bhk_choices,            # Dynamic BHK
        
        # Selected values for UI state
        "selected_amenities": amenities,
        "selected_status": status,
        "selected_bhk": bhk,
    }

    return render(request, "projects/residential_list.html", context)


def project_details(request, id, slug):
    project = get_object_or_404(Project, id=id, slug=slug, active=True)

    # ================= CURRENT PROJECT CARPET =================
    carpet_range = project.configurations.aggregate(
        min_area=Min("area_sqft"),
        max_area=Max("area_sqft")
    )

    # ================= RELATED PROJECTS (SAME LOCALITY) =================
    related_projects = (
            Project.objects
            .filter(active=True)
            .exclude(id=project.id)
            .filter(
                Q(locality=project.locality) |      # same locality
                Q(city=project.city) |              # same city
                Q(developer=project.developer)      # same developer
            )
            .annotate(
                min_carpet=Min("configurations__area_sqft"),
                max_carpet=Max("configurations__area_sqft"),
                min_price=Min("configurations__price_in_rupees"),
            )
            .select_related("city", "locality", "developer")
            .prefetch_related("configurations")
            .distinct()[:8]
        )
    # ================= FALLBACK → SAME CITY =================
    if not related_projects.exists():
        related_projects = (
            Project.objects
            .filter(active=True, city=project.city)
            .exclude(id=project.id)
            .annotate(
                min_carpet=Min("configurations__area_sqft"),
                max_carpet=Max("configurations__area_sqft"),
                min_price=Min("configurations__price_in_rupees"),
            )
        )

    related_projects = related_projects[:8]

    context = {
        "project": project,
        "min_carpet": carpet_range["min_area"],
        "max_carpet": carpet_range["max_area"],
        "related_projects": related_projects,
        "project_faqs": project.faqs.all().order_by("order"),
    }

    return render(request, "projects/project_detail.html", context)

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

def project_details(request, id, slug):

    # ✅ STEP 1: FETCH PROJECT FIRST
    project = get_object_or_404(Project, id=id, slug=slug, active=True)

    # ✅ STEP 2: SETTINGS
    settings_obj = Setting.objects.first()
    rs = Setting.objects.first()

    # ✅ STEP 3: CARPET RANGE
    carpet_range = project.configurations.aggregate(
        min_area=Min("area_sqft"),
        max_area=Max("area_sqft")
    )

    # ✅ STEP 4: RELATED PROJECTS (LOCALITY FIRST)
    related_projects = Project.objects.filter(
        locality=project.locality,
        active=True
    ).exclude(id=project.id)

    # 👉 Fallback: agar same locality me aur project na mile
    if not related_projects.exists():
        related_projects = Project.objects.filter(
            city=project.city,
            active=True
        ).exclude(id=project.id)

    related_projects = related_projects[:8]

    # ✅ STEP 5: FAQ
    project_faqs = project.faqs.all().order_by("order")

    # ✅ STEP 6: FINAL CONTEXT
    context = {
        "project": project,
        "active": project,

        "settings_obj": settings_obj,
        "rs": rs,

        "min_carpet": carpet_range["min_area"],
        "max_carpet": carpet_range["max_area"],

        "welcome": project.welcomes.all(),
        "usps": project.usps.all(),
        "configurations": project.configurations.all().order_by("bhk_type"),
        "gallery": project.gallery.all(),
        "amenities": project.amenities.all(),
        "rera": project.rera.all(),
        "BookingOffer": project.BookingOffer.all(),
        "headers": project.headers.all(),
        "configs": project.configurations.all(),
        "why_invest": project.why_invest.all(),

        # ✅ RELATED + FAQ
        "project_faqs": project_faqs,
        "related_projects": related_projects,

        # OPTIONAL
        "properties": Property.objects.filter(project=project),
    }

    return render(request, "projects/project_detail.html", context)

def submit_enquiry(request, id):
    project = get_object_or_404(Project, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Save enquiry
        Enquiry.objects.create(
            project=project,
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        messages.success(request, "Thank you! Your enquiry has been submitted successfully.")
        return redirect('thank_you')  # or use project detail slug redirect

    return redirect('project_details', id=project.id, slug=project.slug)

def thank_you(request):
    return render(request, 'projects/thank_you.html')

def load_localities(request):
    city_id = request.GET.get("city_id")
    localities = Locality.objects.filter(city_id=city_id).values("id", "name")
    return JsonResponse(list(localities), safe=False)

