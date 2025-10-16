from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.utils.html import mark_safe
# Create your models here.
from django.db.models import Avg, Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.utils.text import slugify
from utility.models import City,Locality,PossessionIn,PropertyType,ProjectAmenities,Bank
from multiselectfield import MultiSelectField
from user.models import Developer
from embed_video.fields import EmbedVideoField



# --- Helper Function for Price Formatting ---
def format_price(num):
    """Convert number into Indian readable format (Lac/Cr)."""
    # Price comes as a string, convert it carefully
    try:
        num = int("".join(filter(str.isdigit, str(num))))
    except ValueError:
        return ""

    if num >= 10000000:  # 1 Crore
        return f"{round(num/10000000, 2):.2f} Cr"
    elif num >= 100000:  # 1 Lac
        return f"{round(num/100000, 2):.2f} L"
    else:
        # Using the standard format for numbers less than 1 Lakh
        return f"{num: ,}"
# --------------------------------------------


class Project(MPTTModel):
    
    BHK_CHOICES = (
        ('1 BHK', '1 BHK'), ('2 BHK', '2 BHK'), ('3 BHK', '3 BHK'), ('5 BHK', '5 BHK'), 
        ('6 BHK', '6 BHK'), ('7 BHK', '7 BHK'), ('8 BHK', '8 BHK'), ('9 BHK', '9 BHK'),
        ('10 BHK', '10 BHK'), ('10+ BHK', '10+ BHK'),
    )

    Construction_Status = (
        ('Under Construction', 'Under Construction'), ('New Launch', 'New Launch'),
        ('Partially Ready To Move', 'Partially Ready To Move'), ('Ready To Move', 'Ready To Move'),
        ('Deleverd', 'Deleverd'),
    )
    
    MONTH_CHOICES = [
        ('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), 
        ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'),
        ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December'),
    ]
    
    Occupancy_Certificate = (('Yes', 'Yes'),('No', 'No'), )
    Commencement_Certificate = (('Yes', 'Yes'),('No', 'No'),)
    
    # --- Project Core Fields ---
    Occupancy_Certificate = models.CharField(max_length=25, choices=Occupancy_Certificate,null=True, blank=True)
    Commencement_Certificate = models.CharField(max_length=25, choices=Commencement_Certificate,null=True, blank=True)
    
    construction_status = models.CharField(max_length=25, choices=Construction_Status)
    propert_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE) 

    # MPTT Hierarchy
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=250)
    
    # Foreign Keys
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE) 
    city = models.ForeignKey(City, on_delete=models.CASCADE) 
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE) 
    
    land_parce = models.CharField(max_length=50,null=True, blank=True)
    bhk_type = MultiSelectField(choices=BHK_CHOICES, max_length=50,null=True, blank=True)
    floor = models.CharField(max_length=50,null=True, blank=True)
    
    possession_year = models.ForeignKey(PossessionIn, on_delete=models.CASCADE) 
    possession_month = models.CharField(max_length=20, choices=MONTH_CHOICES, blank=True, null=True, help_text="Select Possession Month")
    
    luxurious = models.CharField(max_length=50,null=True, blank=True)
    priceing = models.CharField(max_length=50,null=True, blank=True) 
    youtube_embed_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="YouTube Video ID"
    )
    
    featured_property = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True,upload_to='images/')
    
    slug = models.SlugField(unique=True, null=True, blank=True,max_length=555,)
    create_at = models.DateTimeField(auto_now_add=True,null=True, blank=True,)
    update_at = models.DateTimeField(auto_now=True,null=True, blank=True,)
    
    # --- Overridden Methods ---
    def __str__(self):
        # Uses MPTT logic for full path (e.g., Phase 1 / Block A)
        full_path = [str(node.project_name) for node in self.get_ancestors(include_self=True)]
        return ' / '.join(full_path)
    
    class Meta:
        verbose_name_plural='1. Project'

    # 🔑 CRITICAL FIX: Handling object-to-string conversion for slug creation
    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        # Ensure locality and city objects are safely converted to strings for slugify
        locality_name = str(self.locality) if self.locality else ''
        city_name = str(self.city) if self.city else ''

        base_slug = slugify(f"{self.project_name} {locality_name} {city_name}")
        new_slug = f"{base_slug}-{self.id}"

        if self.slug != new_slug:
            self.slug = new_slug
            # Use update_fields only if saving existing object
            if self.pk:
                super().save(update_fields=['slug'])
            else:
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
    # --- End save method ---

    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" height="50"/>')
        return ""

    class MPTTMeta:
        order_insertion_by = ['project_name']

    def get_absolute_url(self):
        return reverse("project_details", kwargs={'id': self.id, 'slug': self.slug})

    # --- Configuration Summary Methods (Using the format_price helper) ---
    # projects/models.py (Project model ke andar)

    def get_configuration_summary(self):
        configs = self.configurations.all()
        if not configs:
            return ""

        try:
            # Configuration objects se area ki list banao
            areas = [c.area_sqft for c in configs if c.area_sqft is not None]
        except Exception: # Specific error type use karna behtar hai
            areas = []
        
        if not areas:
            return ""

        min_area = min(areas)
        max_area = max(areas)

        # Unique BHK types (sets automatically handle unique values)
        bhk_list = sorted(set([c.bhk_type for c in configs]))
        bhk_display = ", ".join(bhk_list)

        return f"{min_area}-{max_area} Sq.ft ({bhk_display})"

    def get_price_range(self):
        configs = self.configurations.all()
        if not configs:
            return ""

        try:
            # FIX: Sahi IntegerField 'price_in_rupees' use kiya gaya hai.
            # Filter out None values to prevent min()/max() errors
            prices = [c.price_in_rupees for c in configs if c.price_in_rupees is not None]
        except Exception: 
            # Yeh block generic errors ko handle karta hai
            prices = []

        if not prices:
            return ""

        min_price = min(prices)
        max_price = max(prices)

        # format_price function use karein (jo models.py ke top par define kiya gaya hai)
        if min_price == max_price:
            return format_price(min_price)


class BookingOffer(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="BookingOffer")
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class WelcomeTo(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="welcomes")
    description = models.TextField(null=True, blank=True,max_length=5500)
    read_more= models.TextField(null=True, blank=True,max_length=5500)

    def __str__(self):
        return self.description

class Location(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="locations")
    google_map_iframe = models.TextField(null=True, blank=True,)

    def __str__(self):
        return self.google_map_iframe

class WebSlider(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sliders")
    image = models.ImageField(upload_to='web_slider/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.caption or f"Slider #{self.pk}"

class Overview(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="overviews")
    heading = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.heading

class AboutUs(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="aboutus")
    content = models.TextField()

    def __str__(self):
        return "About Us"

class USP(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="usps")
    point = models.CharField(null=True, blank=True,max_length=150)
    def __str__(self):
        return self.point

class Configuration(models.Model):
    Project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="configurations")
    bhk_type = models.CharField(max_length=50)
    area_sqft = models.IntegerField(
        verbose_name="Area (Sq.ft)",
        help_text="Enter area in numeric square feet."
    ) 
    
    # ✅ Sudhar 3: Price ko IntegerField banayein
    # Yeh lakh/crore calculations ke liye zaroori hai.
    price_in_rupees = models.IntegerField(
        verbose_name="Price (in ₹)",
        help_text="Enter price in total rupees (e.g., 5000000)."
    )

    def __str__(self):
        return f"{self.Project.project_name} - {self.bhk_type} ({self.area_sqft} sq.ft)"
    
    class Meta:
        # Configuration ke instances ko Project aur BHK type ke hisaab se arrange karein
        ordering = ['bhk_type']

class Connectivity(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="configs")
    title = models.CharField(max_length=50)


    def __str__(self):
        return f"{self.title}"

class Amenities(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="amenities")
    amenities = models.ForeignKey(ProjectAmenities, on_delete=models.CASCADE, related_name="amenities")
    
    def __str__(self):
        return f"{self.Project.project_name} - {self.amenities.title}"

class Gallery(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to='gallery/')

    def __str__(self):
        return f"Image #{self.pk}"

class Header(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="headers")    
    title = models.CharField(max_length=2000,null=True, blank=True)
    keywords = models.CharField(max_length=2000,null=True, blank=True)
    meta_description = models.CharField(max_length=5000,null=True, blank=True)
    logo = models.ImageField(null=True, blank=True,upload_to='images/')
    welcome_to_bg = models.ImageField(null=True, blank=True,upload_to='headers/')
    virtual_site_visit_bg = models.ImageField(null=True, blank=True,upload_to='headers/')
    schedule_a_site_visit = models.ImageField(null=True, blank=True,upload_to='headers/')

    def __str__(self):
        return self.keywords

class RERA_Info(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="rera")
    qr_image = models.ImageField(null=True, blank=True,upload_to='overviewimage/')
    registration_no= models.CharField(null=True, blank=True,max_length=50)
    project_registered = models.CharField(null=True, blank=True,max_length=50)
    government_rera_authorised_advertiser = models.CharField(null=True, blank=True,max_length=150)
    site_address  = models.CharField(null=True, blank=True,max_length=500)
    contact_us= models.CharField(null=True, blank=True,max_length=500)
    disclaimer= models.CharField(null=True, blank=True,max_length=1500)
    document = models.FileField(null=True, blank=True,upload_to='rera_docs/')

    def __str__(self):
        return self.registration_no

class WhyInvest(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="why_invest")
    title = models.CharField(max_length=350,null=True, blank=True)
    discripation = models.CharField(max_length=500,null=True, blank=True)
    

    def __str__(self):
        return f"Why Invest - {self.pk}"
 
class BankOffer(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="amenities")
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="amenities")
    
    def __str__(self):
        return f"{self.Project.project_name} - {self.bank.title}"

    

class BankOffer(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bank_offers")
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="bank_offers")
    
    def __str__(self):
        return f"{self.Project.project_name} - {self.bank.title}"


