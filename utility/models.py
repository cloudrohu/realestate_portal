# utility/models.py
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify

class City(MPTTModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    
    # MPTT Hierarchy Field: Yeh field define karta hai ki kaun kiska parent hai.
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='Parent Location (State/City)'
    )
    
    # Level Type se aap identify kar sakte hain ki yeh entry kya hai (City, Locality, etc.)
    level_choices = (
        ('STATE', 'State/Province'),
        ('CITY', 'City'),
        ('LOCALITY', 'Locality/Sector'),
        ('AREA', 'Sub-Area/Zone'),
    )
    level_type = models.CharField(max_length=20, choices=level_choices, default='LOCALITY')

    class MPTTMeta:
        # Hierarchy ko name ke hisaab se sort karega
        order_insertion_by = ['name']
    
    class Meta:
        verbose_name = "Location (City/Locality)"
        verbose_name_plural = "Locations (Cities/Localities)"

    def __str__(self):
        # Admin mein hierarchy path dikhayega (e.g., Delhi / Vasant Kunj)
        full_path = [node.name for node in self.get_ancestors(include_self=True)]
        return ' / '.join(full_path)
# --- 2. Locality Model (MPTT Child Structure) ---
class Locality(MPTTModel):
    # Standard Foreign Key to City (This is the explicit geographical link)
    city = models.ForeignKey(City, on_delete=models.CASCADE) 
    
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    
    # MPTT Hierarchy Field: Allows Locality to have sub-localities (e.g., Phase 1 > Block A)
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='Parent Locality/Zone'
    )

    class MPTTMeta:
        order_insertion_by = ['name']
        unique_together = ('city', 'name') # Ensures locality name is unique within a City

    def __str__(self):
        # Shows Local Sub-hierarchy + City link
        path = [node.name for node in self.get_ancestors(include_self=True)]
        return f"{' / '.join(path)} ({self.city.name})"
# ... (Keep Developer, Bank, P_Amenities models here) ...
# --- PropertyType Model (MPTT) ---
class PropertyType(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    
    # Hierarchy Field: Allows parent/child relationships
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='Parent Type/Category'
    )
    
    # Flag to easily identify main categories (Residential/Commercial) in views
    is_top_level = models.BooleanField(default=False) 
    
    # Flag to denote if this type can be directly selected for a listing (e.g., "3 BHK" can be selected, but "Residential" cannot)
    is_selectable = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "Property Types"

    def __str__(self):
    # Sahi syntax: Sirf string separator (' / ') ko join method se pehle use karein.
        full_path = [node.name for node in self.get_ancestors(include_self=True)]
        return ' / '.join(full_path) # <-- **Is tarah theek karein**
# --- Property Model (Ensure the FK is pointing here) ---
class Property(models.Model):
    # Link to the MPTT Type
    property_type = models.ForeignKey(PropertyType, on_delete=models.PROTECT) 

    # Link to Location
    city = models.ForeignKey('utility.City', on_delete=models.PROTECT) 
    locality = models.ForeignKey('utility.Locality', on_delete=models.PROTECT) 

    # ... (Other fields like title, price, bedrooms, etc.) ...
# --- PossessionIn Model (Only Year) ---
class PossessionIn(models.Model):
    year = models.PositiveIntegerField(
        unique=True,
        help_text="e.g. 2025"
    )

    class Meta:
        verbose_name = "Possession Year"
        verbose_name_plural = "Possession Years"
        ordering = ['year']

    def __str__(self):
        return str(self.year)

class ProjectAmenities(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='amenities/', blank=True, null=True)



    def __str__(self):
        return self.title

class Bank(models.Model):
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(upload_to='images/')
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural='03. Bank'