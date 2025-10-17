from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django.utils.html import mark_safe
from .models import City, Locality, PropertyType, PossessionIn, ProjectAmenities, Bank, Property

# 🟡 Placeholder image URL (fallback)
NO_IMAGE_URL = "https://via.placeholder.com/80x80.png?text=No+Image"


# --------------------------------------------
# 🏙 City Admin (MPTT)
# --------------------------------------------
@admin.register(City)
class CityAdmin(MPTTModelAdmin):
    list_display = ('name', 'level_type', 'parent')
    list_filter = ('level_type',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    mptt_level_indent = 20

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'parent', 'level_type')
        }),
    )


# --------------------------------------------
# 📍 Locality Admin (MPTT)
# --------------------------------------------
@admin.register(Locality)
class LocalityAdmin(MPTTModelAdmin):
    list_display = ('name', 'city', 'parent')
    list_filter = ('city',)
    search_fields = ('name', 'city__name')
    prepopulated_fields = {"slug": ("name",)}
    mptt_level_indent = 20

    fieldsets = (
        ('Basic Info', {
            'fields': ('city', 'name', 'slug', 'parent')
        }),
    )


# --------------------------------------------
# 🏠 PropertyType Admin (MPTT)
# --------------------------------------------
@admin.register(PropertyType)
class PropertyTypeAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'is_top_level', 'is_selectable')
    list_filter = ('is_top_level', 'is_selectable')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    mptt_level_indent = 20

    fieldsets = (
        ('Property Type Info', {
            'fields': ('name', 'slug', 'parent', 'is_top_level', 'is_selectable')
        }),
    )


# --------------------------------------------
# 📅 PossessionIn Admin
# --------------------------------------------
@admin.register(PossessionIn)
class PossessionInAdmin(admin.ModelAdmin):
    list_display = ('year',)
    ordering = ('year',)
    search_fields = ('year',)


# --------------------------------------------
# 🏊 Project Amenities Admin
# --------------------------------------------
@admin.register(ProjectAmenities)
class ProjectAmenitiesAdmin(admin.ModelAdmin):
    list_display = ('title', )
    


# --------------------------------------------
# 🏦 Bank Admin
# --------------------------------------------
@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview')
    search_fields = ('title',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
        else:
            url = NO_IMAGE_URL
        return mark_safe(f'<img src="{url}" width="60" height="60" style="object-fit:contain;border-radius:6px;" />')
    image_preview.short_description = "Logo"


# --------------------------------------------
# 📝 Property (Optional Basic Admin)
# --------------------------------------------
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_type', 'city', 'locality')
    list_filter = ('property_type', 'city', 'locality')
    search_fields = ('property_type__name', 'city__name', 'locality__name')
