from django.contrib import admin
from django.utils.html import mark_safe
from .models import PropertyAmenities, FurnishingItem, Facility, TenantType

# Placeholder image
NO_IMAGE_URL = "https://via.placeholder.com/40x40.png?text=No+Image"


# =======================================================
# 🏠 Property Amenities Admin
# =======================================================


@admin.register(PropertyAmenities)
class PropertyAmenitiesAdmin(admin.ModelAdmin):

    list_display = ('name', 'icon_preview')
    search_fields = ('name',)
    readonly_fields = ('icon_preview',)

    def icon_preview(self, obj):
        if obj.icon:
            try:
                url = obj.icon.url
            except:
                url = obj.icon
            return mark_safe(
                f'<img src="{url}" width="40" height="40" style="object-fit:contain;border-radius:4px;" />'
            )
        return mark_safe(f'<img src="{NO_IMAGE_URL}" width="40">')

    icon_preview.short_description = "Icon"

# =======================================================
# 🛋 Furnishing Item Admin
# =======================================================

@admin.register(FurnishingItem)
class FurnishingItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_active', 'icon_preview')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('icon_preview',)

    def icon_preview(self, obj):
        if obj.icon:
            try:
                url = obj.icon.url
            except:
                url = obj.icon
            return mark_safe(
                f'<img src="{url}" width="40" height="40" style="object-fit:contain;border-radius:4px;" />'
            )
        return mark_safe(f'<img src="{NO_IMAGE_URL}" width="40">')

    icon_preview.short_description = "Icon"


# =======================================================
# 🏢 Facility Admin
# =======================================================
@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):

    list_display = ('name', 'icon', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(TenantType)
class TenantTypeAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)