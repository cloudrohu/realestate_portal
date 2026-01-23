from django.contrib import messages
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
    
    return render(request, 'projects/projects.html', context)

def get_bhk_choices():
    return [choice[0] for choice in Project.BHK_CHOICES]

def search_projects(request):
    settings_obj = Setting.objects.first()

    location = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    amenities = request.GET.get("amenities")
    status = request.GET.get("construction_status")
    bhk = request.GET.get("bhk")

    locality_ids = request.GET.getlist("locality")

    projects = Project.objects.filter(active=True)

    if location:
        search_term = location.split(",")[0].strip()
        projects = projects.filter(
            Q(project_name__icontains=search_term) |
            Q(locality__name__icontains=search_term) |
            Q(city__name__icontains=search_term)
        )

    if city:
        projects = projects.filter(city__name__iexact=city)

    if locality_ids:
        selected_localities = Locality.objects.filter(id__in=locality_ids)

        all_localities = Locality.objects.none()
        for loc in selected_localities:
            all_localities |= loc.get_descendants(include_self=True)

        projects = projects.filter(locality__in=all_localities).distinct()

    # ✅ Amenities Filter (FIXED)
    if amenities:
        amenity_list = [a.strip() for a in amenities.split(",") if a.strip()]
        if amenity_list:
            projects = projects.filter(
                project_amenities__amenities__title__in=amenity_list
            ).distinct()

    # ✅ Status Filter
    if status:
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        if status_list:
            projects = projects.filter(construction_status__in=status_list).distinct()

    # ✅ BHK Filter
    selected_bhk_list = []
    if bhk:
        selected_bhk_list = [b.strip() for b in bhk.split(",") if b.strip()]
        if selected_bhk_list:
            bhk_query = Q()
            for b in selected_bhk_list:
                bhk_query |= Q(bhk_type__icontains=b) | Q(configurations__bhk_type__icontains=b)
            projects = projects.filter(bhk_query).distinct()

    # ✅ Pagination + Optimize (FIXED)
    projects = projects.select_related("city", "locality")\
        .prefetch_related("project_amenities__amenities")\
        .order_by("-create_at")

    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    context = {
        "projects": projects_page,
        "settings_obj": settings_obj,
        "amenities": ProjectAmenities.objects.all(),
        "construction_status": [choice[0] for choice in Project.Construction_Status],
        "bhk_choices": get_bhk_choices(),
        "selected_amenities": amenities,
        "selected_status": status,
        "selected_bhk": bhk,
        "selected_bhk_list": selected_bhk_list,
        "available_localities": Locality.objects.all().order_by("name"),
        "selected_locality_ids": [str(x) for x in locality_ids],
    }

    return render(request, "projects/residential_list.html", context)
    
def residential_projects(request):
    settings_obj = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "residential").strip()
    bhk = request.GET.get("bhk", "").strip()
    amenities = request.GET.get("amenities", "").strip()
    status = request.GET.get("construction_status", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    rera = request.GET.get("rera", "").strip()

    # ✅ MULTI Locality IDs
    locality_ids = request.GET.getlist("locality")

    # ✅ price safe annotation
    projects = Project.objects.filter(active=True).annotate(
        min_p=Min(
            "configurations__price_in_rupees",
            filter=Q(configurations__price_in_rupees__isnull=False, configurations__price_in_rupees__gt=0)
        ),
        max_p=Max(
            "configurations__price_in_rupees",
            filter=Q(configurations__price_in_rupees__isnull=False, configurations__price_in_rupees__gt=0)
        )
    )

    # ✅ Category
    if category.lower() == "commercial":
        projects = projects.filter(propert_type__parent__name__iexact="Commercial")
    else:
        projects = projects.filter(propert_type__parent__name__iexact="Residential")

    # ✅ Search
    if query:
        projects = projects.filter(
            Q(project_name__icontains=query) |
            Q(locality__name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(developer__name__icontains=query)
        )

    # ✅ ✅ Locality Filter (MPTT)
    if locality_ids:
        selected_localities = Locality.objects.filter(id__in=locality_ids)

        all_localities = Locality.objects.none()
        for loc in selected_localities:
            all_localities |= loc.get_descendants(include_self=True)

        projects = projects.filter(locality__in=all_localities).distinct()

    # ✅ Budget filter
    if min_price or max_price:
        projects = projects.exclude(min_p__isnull=True).exclude(max_p__isnull=True)

    try:
        if min_price:
            min_price_int = int(min_price)
            projects = projects.filter(max_p__gte=min_price_int)

        if max_price:
            max_price_int = int(max_price)
            projects = projects.filter(min_p__lte=max_price_int)
    except ValueError:
        pass

    # ✅ BHK filter
    selected_bhk_list = []
    if bhk:
        selected_bhk_list = [b.strip() for b in bhk.split(",") if b.strip()]
        if selected_bhk_list:
            bhk_query = Q()
            for b in selected_bhk_list:
                bhk_query |= Q(bhk_type__icontains=b) | Q(configurations__bhk_type__icontains=b)
            projects = projects.filter(bhk_query).distinct()

    # ✅ Status filter
    selected_status_list = []
    if status:
        selected_status_list = [s.strip() for s in status.split(",") if s.strip()]
        if selected_status_list:
            projects = projects.filter(construction_status__in=selected_status_list).distinct()

    # ✅ Amenities filter
    selected_amenities_list = []
    if amenities:
        selected_amenities_list = [a.strip() for a in amenities.split(",") if a.strip()]
        if selected_amenities_list:
            projects = projects.filter(
                project_amenities__amenities__title__in=selected_amenities_list
            ).distinct()


    # ✅ RERA filter
    if rera:
        projects = projects.filter(rera__registration_no__isnull=False).exclude(rera__registration_no="").distinct()

    projects = projects.select_related("city", "locality", "developer").prefetch_related(
        "project_amenities__amenities", "configurations"
    ).order_by("-create_at").distinct()

    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    selected_locality_ids = [str(x) for x in locality_ids]

    context = {
        "projects": projects_page,
        "settings_obj": settings_obj,

        "amenities": ProjectAmenities.objects.all().order_by("title"),
        "construction_status": [choice[0] for choice in Project.Construction_Status],
        "bhk_choices": [choice[0] for choice in Project.BHK_CHOICES],

        "selected_bhk_list": selected_bhk_list,
        "selected_status_list": selected_status_list,
        "selected_amenities_list": selected_amenities_list,

        "selected_amenities": amenities,
        "values": request.GET,

        # ✅ Locality dynamic list + selected ids
        "available_localities": Locality.objects.all().order_by("name"),
        "selected_locality_ids": selected_locality_ids,
    }
    return render(request, "projects/residential_list.html", context)

def project_details(request, id, slug):
    settings_obj = Setting.objects.first()

    project = get_object_or_404(Project, id=id, slug=slug, active=True)

    carpet_range = project.configurations.aggregate(
        min_area=Min("area_sqft"),
        max_area=Max("area_sqft")
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
            )
        )[:8]

    # ✅ AMENITIES
    project_amenities = project.project_amenities.all().distinct()


    context = {
        "settings_obj": settings_obj,
        "project": project,
        "min_carpet": carpet_range["min_area"],
        "max_carpet": carpet_range["max_area"],
        "related_projects": related_projects,
        "project_faqs": project.faqs.all().order_by("order"),
        "project_amenities": project_amenities,
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
