from django.db import models

# Create your models here.

from projects.models import Project # Import the Project model

class Property(models.Model):
    # Link to Project
    project = models.ForeignKey(
        'projects.Project', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='unit_listings'  # <-- THIS MUST BE DEFINED
    ) 
    
    # Core Details
    title = models.CharField(max_length=200) # E.g., "3 BHK Apartment"
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    sqft = models.IntegerField()
    description = models.TextField(blank=True)
    # Image field
    main_photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    list_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title