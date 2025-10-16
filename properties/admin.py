# properties/admin.py
from django.contrib import admin
from .models import Property

# Hum Admin interface ko customize kar sakte hain
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'price', 'bedrooms', 'is_published', 'list_date')
    list_display_links = ('title',) # Title pe click karke edit kar saken
    list_filter = ('project', 'is_published', 'bedrooms') # Right side mein filter option
    list_editable = ('is_published',) # List view se hi publish status change kar saken
    search_fields = ('title', 'description', 'address')
    list_per_page = 25

admin.site.register(Property, PropertyAdmin)