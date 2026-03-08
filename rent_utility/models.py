from django.db import models

# Create your models here.
class PropertyAmenities(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='property/amenities/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Property Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name

class FurnishingItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Furnishing Item"
        verbose_name_plural = "Furnishing Items"
        ordering = ['name']

    def __str__(self):
        return self.name


class Facility(models.Model):
    
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100,blank=True,null=True,help_text="Enter icon class (e.g. fa-solid fa-car)")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"
        ordering = ['name']

    def __str__(self):
        return self.name


class TenantType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tenant Type"
        verbose_name_plural = "Tenant Types"
        ordering = ['name']

    def __str__(self):
        return self.name

