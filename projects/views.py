from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Min, Max
from django.http import JsonResponse

from home.models import Setting
from properties.models import Property
from utility.models import (
    City, Locality, PropertyType, PossessionIn,
    ProjectAmenities, Bank, PropertyAmenities
)
from .models import (
    Project, Configuration, Gallery, RERA_Info, BookingOffer, Overview,
    USP, Amenities, Header, WelcomeTo, Connectivity, WhyInvest, Enquiry, ProjectFAQ
)

def index(request):
    queryset_list = Project.objects.filter(active=True).order_by('project_name')
    
    if 'city_id' in request.GET and request.GET['city_id']:
        city_id = request.GET['city_id']
        queryset_list = queryset_list.filter(city_id=city_id)

    if 'locality_id' in request.GET and request.GET['locality_id']:
        locality_id = request.GET['locality_id']
        try:
            selected_locality = Locality.objects.get(pk=locality_id)
            descendant_localities = selected_locality.get_descendants(include_self=True)
            queryset_list = queryset_list.filter(locality__in=descendant_localities)
        except Locality.DoesNotExist:
            pass

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
        'values': request.GET,
    }
    
    return render(request, 'home/index.html', context)

def get_bhk_choices():
    return [choice[0] for choice in Project.BHK_CHOICES]

def split_csv(value: str):
    """Convert CSV string -> clean list"""
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

def search_projects(request):
    settings_obj = Setting.objects.first()

    location = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    amenities = request.GET.get("amenities", "")
    status = request.GET.get("construction_status", "")
    bhk = request.GET.get("bhk", "")

    projects = Project.objects.filter(active=True).select_related("city", "locality").prefetch_related("amenities")

    # ✅ Search by text
    if location:
        search_term = location.split(",")[0].strip()
        projects = projects.filter(
            Q(project_name__icontains=search_term) |
            Q(locality__name__icontains=search_term) |
            Q(city__name__icontains=search_term)
        )

    # ✅ City
    if city:
        projects = projects.filter(city__name__iexact=city)

    # ✅ Amenities
    amenity_list = split_csv(amenities)
    if amenity_list:
        projects = projects.filter(amenities__amenities__title__in=amenity_list).distinct()

    # ✅ Construction Status
    status_list = split_csv(status)
    if status_list:
        projects = projects.filter(construction_status__in=status_list).distinct()

    # ✅ BHK Filter ✅
    selected_bhk_list = split_csv(bhk)
    if selected_bhk_list:
        bhk_query = Q()
        for b in selected_bhk_list:
            bhk_query |= Q(bhk_type__icontains=b)  # MultiSelectField stored as string
            bhk_query |= Q(configurations__bhk_type__iexact=b)
        projects = projects.filter(bhk_query).distinct()

    # ✅ Pagination
    projects = projects.order_by("-create_at")
    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    context = {
        "projects": projects_page,
        "settings_obj": settings_obj,

        # options
        "amenities": ProjectAmenities.objects.all(),
        "construction_status": [choice[0] for choice in Project.Construction_Status],
        "bhk_choices": get_bhk_choices(),

        # selected (UI)
        "selected_amenities": amenities,
        "selected_status": status,
        "selected_bhk": bhk,
        "selected_bhk_list": selected_bhk_list,
    }

    return render(request, "projects/residential_list.html", context)

def residential_projects(request):
    settings_obj = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    bhk = request.GET.get("bhk", "")
    amenities = request.GET.get("amenities", "")
    status = request.GET.get("construction_status", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")

    projects = (
        Project.objects
        .filter(propert_type__parent__name__iexact="Residential", active=True)
        .select_related("city", "locality", "propert_type", "developer")
        .prefetch_related("amenities", "configurations")
        .annotate(
            min_price=Min("configurations__price_in_rupees"),
            max_price=Max("configurations__price_in_rupees"),
        )
    )

    # ✅ Search
    if query:
        projects = projects.filter(
            Q(project_name__icontains=query) |
            Q(locality__name__icontains=query) |
            Q(city__name__icontains=query)
        )

    # ✅ Price Filter
    if min_price.isdigit():
        projects = projects.filter(max_price__gte=int(min_price))

    if max_price.isdigit():
        projects = projects.filter(min_price__lte=int(max_price))

    # ✅ Amenities Filter
    selected_amenities_list = split_csv(amenities)
    if selected_amenities_list:
        projects = projects.filter(
            amenities__amenities__title__in=selected_amenities_list
        ).distinct()

    # ✅ Status Filter
    selected_status_list = split_csv(status)
    if selected_status_list:
        projects = projects.filter(
            construction_status__in=selected_status_list
        ).distinct()

    # ✅ BHK Filter ✅ MAIN ✅
    selected_bhk_list = split_csv(bhk)
    if selected_bhk_list:
        bhk_query = Q()
        for b in selected_bhk_list:
            bhk_query |= Q(configurations__bhk_type__iexact=b)
            bhk_query |= Q(bhk_type__icontains=b)
        projects = projects.filter(bhk_query).distinct()

    # ✅ Pagination
    projects = projects.order_by("-create_at")
    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    context = {
        "projects": projects_page,
        "settings_obj": settings_obj,
        "page_title": "Residential Projects",
        "breadcrumb": "Residential",

        # filter options
        "amenities": ProjectAmenities.objects.all().order_by("title"),
        "construction_status": [choice[0] for choice in Project.Construction_Status],
        "bhk_choices": get_bhk_choices(),

        # selected
        "selected_amenities": amenities,
        "selected_amenities_list": selected_amenities_list,

        "selected_status": status,
        "selected_status_list": selected_status_list,

        "selected_bhk": bhk,
        "selected_bhk_list": selected_bhk_list,

        "values": request.GET,
    }

    return render(request, "projects/residential_list.html", context)

def project_details(request, id, slug):
    project = get_object_or_404(Project, id=id, slug=slug, active=True)

    carpet_range = project.configurations.aggregate(
        min_area=Min("area_sqft"),
        max_area=Max("area_sqft"),
    )

    related_projects = (
        Project.objects
        .filter(active=True)
        .exclude(id=project.id)
        .filter(
            Q(locality=project.locality) |
            Q(city=project.city) |
            Q(developer=project.developer)
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

    if not related_projects.exists():
        related_projects = (
            Project.objects
            .filter(active=True, city=project.city)
            .exclude(id=project.id)
            .annotate(
                min_carpet=Min("configurations__area_sqft"),
                max_carpet=Max("configurations__area_sqft"),
                min_price=Min("configurations__price_in_rupees"),
            )[:8]
        )

    context = {
        "project": project,
        "min_carpet": carpet_range["min_area"],
        "max_carpet": carpet_range["max_area"],
        "related_projects": related_projects,
        "project_faqs": project.faqs.all(),
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

