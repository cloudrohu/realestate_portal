from django.shortcuts import render, redirect, get_object_or_404
from home.models import Setting
from .models import RentalProperty,RentalEnquiry
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rent_utility.models import TenantType,FurnishingItem
from utility.models import Locality

def rent_list(request):

    settings_obj = Setting.objects.first()
    properties = RentalProperty.objects.filter(active=True)
    locality_choices = Locality.objects.all().order_by("name")
    tenant_types = TenantType.objects.filter(is_active=True)
    selected_tenants = request.GET.getlist("tenant")

    posted_by_choices = RentalProperty.POSTED_BY_CHOICES
    selected_posted_by = request.GET.getlist("posted_by")


    selected_localities = request.GET.getlist("locality")

    if selected_localities:
        properties = properties.filter(
            locality__name__in=selected_localities
        )

    if selected_tenants:
        properties = properties.filter(
            tenant_type__id__in=selected_tenants
        )


    selected_furnishing = request.GET.getlist("furnishing")

    if selected_furnishing:
        properties = properties.filter(
            furnishing_type__id__in=selected_furnishing
        )

    selected_bathrooms = request.GET.getlist("bathroom")

    if selected_bathrooms:
        q_obj = Q()

        for val in selected_bathrooms:
            if val == "4+":
                q_obj |= Q(bathrooms__gte=4)
            else:
                q_obj |= Q(bathrooms=int(val))

        properties = properties.filter(q_obj)

    bathroom_choices = [
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4+", "4+"),
    ]

    available_from_choices = RentalProperty.AVAILABLE_FROM_CHOICES
    selected_available_from = request.GET.getlist("available_from")

    if selected_available_from:
        properties = properties.filter(
            available_from__in=selected_available_from
        )

    age_choices = RentalProperty.AGE_OF_PROPERTY_CHOICE
    selected_age = request.GET.getlist("age")

    if selected_age:
        properties = properties.filter(
            age_of_property__in=selected_age
        )

    city_slug = request.GET.get("city")  # agar city filter use kar rahe ho

    if city_slug:
        recent_properties = RentalProperty.objects.filter(
            active=True,
            city__slug=city_slug
        ).order_by("-created_at")[:4]
    else:
        recent_properties = RentalProperty.objects.filter(
            active=True
        ).order_by("-created_at")[:4]

    recent_properties = properties.order_by("-created_at")[:4]

    search_query = request.GET.get("q")

    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(locality__name__icontains=search_query) |
            Q(city__name__icontains=search_query)
        ).distinct()


    context = {
        "settings_obj": settings_obj,
        "properties": properties,
        "locality_choices": locality_choices,
        "selected_localities": selected_localities,
        "tenant_types": tenant_types,
        "selected_tenants": selected_tenants,
        "posted_by_choices": posted_by_choices,
        "selected_posted_by": selected_posted_by,
        "furnishing_items": FurnishingItem.objects.all(),
        "selected_furnishing": selected_furnishing,
        "bathroom_choices": bathroom_choices,
        "selected_bathrooms": selected_bathrooms,
        "available_from_choices": available_from_choices,
        "selected_available_from": selected_available_from,
        "age_choices": age_choices,
        "selected_age": selected_age,
        "recent_properties": recent_properties,
    }

    return render(request, "rent/rent_list.html", context)

def rental_detail(request, slug):
    settings_obj = Setting.objects.first()

    property_obj = get_object_or_404(
        RentalProperty.objects.select_related(
            "rent_details",
            "city",
            "locality",
            "project",
            "tenant_type",
            "furnishing_type",
        ).prefetch_related(
            "connectivities",
            "amenities",
            "furnishings",
            "facilities",
            "owner_details",
            "faqs",
        ),
        slug=slug,
        active=True
    )

    if "enquiry_submit" in request.POST:
        RentalEnquiry.objects.create(
            rental=property_obj,
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message"),
        )
        return redirect("rent_thank_you")

    # 🔥 Handle Enquiry Form Submit
    if request.method == "POST":
        RentalEnquiry.objects.create(
            rental=property_obj,
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message"),
        )
        return redirect("rent_thank_you")

    # 🔥 Recommended Properties (Optimized)
    recommended_properties = RentalProperty.objects.select_related(
        "rent_details", "city", "locality"
    ).filter(
        active=True,
        city=property_obj.city
    ).exclude(id=property_obj.id)[:6]

    search_query = request.GET.get("q")


    return render(request, 'rent/rental_detail.html', {
        "settings_obj": settings_obj,
        "property": property_obj,
        "recommended_properties": recommended_properties
    })


def rent_thank_you(request):
    return render(request, "projects/thank_you.html")