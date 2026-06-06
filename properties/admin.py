# properties/admin.py
from django.contrib import admin
from .models import Property
from import_export.admin import ImportExportModelAdmin

# Hum Admin interface ko customize kar sakte hain
class PropertyAdmin(ImportExportModelAdmin):
    list_display = ('title', 'project', 'price')
    list_filter = ('project',)
    list_editable = ()

admin.site.register(Property, PropertyAdmin)