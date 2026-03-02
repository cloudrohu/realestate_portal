from django.db import models
from django.db import models
from django.utils.text import slugify
from utility.models import City, Locality
from rent_utility.models import FurnishingItem,TenantType,Facility
from properties.models import Project
from utility.models import PropertyAmenities


class RentalProperty(models.Model):

    POSTED_BY_CHOICES = [
        ("Owner", "Owner"),
        ("Builder", "Builder"),
        ("Dealer", "Dealer"),
        ("Feature Dealer", "Feature Dealer"),
    ]

    AVAILABLE_FROM_CHOICES = [
        ("Any Time", "Any Time"),
        ("Immediately", "Immediately"),
        ("Within 15 Days", "Within 15 Days"),
        ("Within 1 Month", "Within 1 Month"),
        ("Within 3 Months", "Within 3 Months"),
        ("After 3 Months", "After 3 Months"),

    ]

    AGE_OF_PROPERTY_CHOICE = [
        ("0-1 years old", "0-1 years old"),
        ("1-5 years old", "1-5 years old"),
        ("5-10 years old", "5-10 years old"),
        ("10+ years old", "10+ years old"),
        ("20+ years old", "20+ years old"),

    ]

    NO_OF_BATHROOM_CHOICE = [
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4+", "4+"),
    ]

    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project,on_delete=models.SET_NULL,null=True,blank=True,related_name="rental_properties")
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    tenant_type = models.ForeignKey(TenantType,on_delete=models.SET_NULL,null=True,blank=True)
    super_area = models.PositiveIntegerField(help_text="Area in Sq.ft")
    floor = models.CharField(max_length=255,null=True,blank=True)
    furnishing_type = models.ForeignKey(FurnishingItem,on_delete=models.SET_NULL,null=True,blank=True)
    posted_by = models.CharField(max_length=20,choices=POSTED_BY_CHOICES,default="Owner",null=True,blank=True)
    available_from = models.CharField(max_length=30,choices=AVAILABLE_FROM_CHOICES,default="Any Time",blank=True)
    age_of_property = models.CharField(max_length=20,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    locality = models.ForeignKey(Locality,on_delete=models.SET_NULL,null=True,blank=True)
    slug = models.SlugField(unique=True, blank=True)
    google_map_iframe = models.TextField(null=True,blank=True)
    youtube_embed_id = models.CharField(max_length=50, blank=True, null=True,verbose_name="YouTube Video ID")
    featured_property = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True,upload_to='images/')
    banner_img = models.ImageField(null=True, blank=True,upload_to='banner_img/')
    master_plan = models.ImageField(null=True, blank=True,upload_to='images/')
    floor_plan = models.ImageField(null=True, blank=True,upload_to='images/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f"{self.title}-{self.city.name}"
            if self.locality:
                base_slug += f"-{self.locality.name}"

            self.slug = slugify(base_slug)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class AboutProperty(models.Model):

    rental = models.OneToOneField('RentalProperty',on_delete=models.CASCADE,related_name='about_section')
    about_title = models.CharField(max_length=255, blank=True, null=True)
    about_description = models.TextField(blank=True, null=True)
    about_readmore = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.rental.title
    
class RentalConnectivity(models.Model):
    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name='connectivities')
    title = models.CharField(max_length=255)
    distance = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} - {self.distance}"

class RentalAmenity(models.Model):
    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name='amenities')
    amenity = models.ForeignKey(PropertyAmenities,on_delete=models.CASCADE,related_name='rental_amenity_items')
    class Meta:
        unique_together = ('rental', 'amenity')

    def __str__(self):
        return f"{self.rental.title} - {self.amenity.name}"

class RentalFurnishing(models.Model):

    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name='furnishings')
    item = models.ForeignKey(FurnishingItem,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('rental', 'item')

    def __str__(self):
        return f"{self.item.name} ({self.quantity})"

class RentalFacility(models.Model):

    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name='facilities')

    facility = models.ForeignKey(Facility,on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1,blank=True,null=True)

    class Meta:
        unique_together = ('rental', 'facility')

    def __str__(self):
        if self.quantity:
            return f"{self.facility.name} ({self.quantity})"
        return self.facility.name
    
class OwnerDetails(models.Model):

    OWNER_TYPE_CHOICES = (
        ('Individual', 'Individual Owner'),
        ('Dealer', 'Property Dealer'),
    )

    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name='owner_details')

    name = models.CharField(max_length=150)

    owner_type = models.CharField(max_length=20,choices=OWNER_TYPE_CHOICES,default='Individual')

    phone = models.CharField(max_length=15)

    locality = models.CharField(max_length=150,blank=True,null=True)

    profile_image = models.ImageField(upload_to='owners/',blank=True,null=True)

    is_online = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RentDetails(models.Model):
    rental = models.OneToOneField("RentalProperty",on_delete=models.CASCADE,related_name="rent_details")

    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    available_from = models.DateField()

    PREFERRED_TENANT_CHOICES = [
        ("Family", "Family"),
        ("Bachelors", "Bachelors"),
        ("Family/Bachelors", "Family / Bachelors"),
    ]

    preferred_tenant = models.CharField(max_length=30,choices=PREFERRED_TENANT_CHOICES)

    lease_duration = models.PositiveIntegerField(help_text="In Months")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rent Details - {self.rental.title}"

class RentalFAQ(models.Model):
    rental = models.ForeignKey("RentalProperty",on_delete=models.CASCADE,related_name="faqs")

    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question   
    

# ------ Enquiry Form ------ #
class RentalEnquiry(models.Model):

    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name="enquiries")

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rental.title}"

class VisitSchedule(models.Model):
    
    rental = models.ForeignKey(RentalProperty,on_delete=models.CASCADE,related_name="visit_requests")

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    visit_date = models.DateField()
    visit_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rental.title}"
