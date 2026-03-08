from django.contrib import admin
from django.utils.html import mark_safe
from .models import RentalProperty, AboutProperty, RentalConnectivity, RentalAmenity, RentalFurnishing,RentalFacility,OwnerDetails,RentDetails,RentalFAQ,RentalEnquiry
from utility.models import PropertyAmenities



class AboutPropertyInline(admin.StackedInline):
    model = AboutProperty
    extra = 0
    verbose_name = "About This Property"
    verbose_name_plural = "About This Property"

class RentalConnectivityInline(admin.TabularInline):
    model = RentalConnectivity
    extra = 1

class RentalAmenityInline(admin.TabularInline):
    model = RentalAmenity
    extra = 1
    autocomplete_fields = ['amenity']

class RentalFurnishingInline(admin.TabularInline):
    model = RentalFurnishing
    extra = 1
    autocomplete_fields = ['item']

class RentalFacilityInline(admin.TabularInline):
    model = RentalFacility
    extra = 1
    autocomplete_fields = ['facility']

class OwnerDetailsInline(admin.StackedInline):
    model = OwnerDetails   # ✅ correct model
    extra = 0

class RentDetailsInline(admin.StackedInline):
    model = RentDetails
    extra = 0

class RentalFAQInline(admin.TabularInline):
    model = RentalFAQ
    extra = 1

@admin.register(RentalProperty)
class RentalPropertyAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'city',
        'locality',
        'project',
        'bedrooms',
        'bathrooms',
        'super_area',
        'tenant_type',
        'created_at',
    )

    list_filter = (
        'city',
        'locality',
        'project',
        'tenant_type',
        'furnishing_type',
    )

    search_fields = (
        'title',
        'city__name',
        'locality__name',
        'project__project_name',
    )


    ordering = ('-created_at',)

    readonly_fields = (
        'slug',
        'created_at',
        'updated_at',
    )

    inlines = [
        AboutPropertyInline,
        RentalConnectivityInline,
        RentalAmenityInline,
        RentalFurnishingInline,
        RentalFacilityInline,
        OwnerDetailsInline,
        RentDetailsInline,
        RentalFAQInline,

    ]

    fieldsets = (

        ('Basic Info', {
            'classes': ('wide',),
            'fields': (
                'title',
                'city',
                'locality',
                'project',
                'slug',
                'active',
            )
        }),

        ('Property Details', {
            'classes': ('wide',),
            'fields': (
                'bedrooms',
                'bathrooms',
                'super_area',
                'furnishing_type',
                'age_of_property',
                'posted_by',
                'available_from',
                'tenant_type',
                'floor',
                'address',
            )
        }),

        ('Images & Media', {
            'fields': (
                'image',
                'master_plan',
                'banner_img',
                'floor_plan',
                'youtube_embed_id',
            )
        }),

        ('Google Map Location', {
            'classes': ('collapse',),
            'fields': (
                'google_map_iframe',
            )
        }),

        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )


@admin.register(RentalEnquiry)
class RentalEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name','phone','rental','created_at')
    search_fields = ('name','phone','email')
    list_filter = ('created_at',)