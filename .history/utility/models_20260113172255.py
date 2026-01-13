# utility/models.py

from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor_uploader.fields import RichTextUploadingField

from projects.models import Project


# =====================================================
# ✅ City (MPTT)
# =====================================================
class City(MPTTModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Location (State/City)'
    )

    level_choices = (
        ('STATE', 'State/Province'),
        ('CITY', 'City'),
        ('LOCALITY', 'Locality/Sector'),
        ('AREA', 'Sub-Area/Zone'),
    )
    level_type = models.CharField(max_length=20, choices=level_choices, default='LOCALITY')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Location (City/Locality)"
        verbose_name_plural = "Locations (Cities/Localities)"

    def __str__(self):
        full_path = [node.name for node in self.get_ancestors(include_self=True)]
        return ' / '.join(full_path)


# =====================================================
# ✅ Locality (MPTT)
# =====================================================
class Locality(MPTTModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    featured_locality = models.BooleanField(default=False)

    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)

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

    class Meta:
        unique_together = ('city', 'name')
        verbose_name_plural = "Localities"

    def __str__(self):
        path = [node.name for node in self.get_ancestors(include_self=True)]
        return f"{' / '.join(path)} ({self.city.name})"


# =====================================================
# ✅ Category (MPTT)
# =====================================================
class Category(MPTTModel):
    parent = TreeForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='children',
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='category/icons/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, null=True)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        full_path = [self.title]
        parent = self.parent
        while parent:
            full_path.append(parent.title)
            parent = parent.parent
        return " / ".join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def icon_tag(self):
        if self.icon:
            return mark_safe(
                f'<img src="{self.icon.url}" style="height:40px;width:40px;object-fit:contain;" />'
            )
        return "—"

    icon_tag.short_description = "Icon"


# =====================================================
# ✅ Sub Locality
# =====================================================
class Sub_Locality(models.Model):
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Sub Locality"

    def get_absolute_url(self):
        return reverse('sub_locality_detail', kwargs={'slug': self.slug})


# =====================================================
# ✅ Property Type (MPTT)
# =====================================================
class PropertyType(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Type/Category'
    )

    is_top_level = models.BooleanField(default=False)
    is_selectable = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "Property Types"

    def __str__(self):
        full_path = [node.name for node in self.get_ancestors(include_self=True)]
        return ' / '.join(full_path)


# =====================================================
# ✅ Possession In
# =====================================================
class PossessionIn(models.Model):
    year = models.PositiveIntegerField(unique=True, help_text="e.g. 2025")

    class Meta:
        verbose_name = "Possession Year"
        verbose_name_plural = "Possession Years"
        ordering = ['year']

    def __str__(self):
        return str(self.year)


# =====================================================
# ✅ Project Amenities
# =====================================================
class ProjectAmenities(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='amenities/', blank=True, null=True)

    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        return ""

    image_tag.short_description = 'Image'

    def __str__(self):
        return self.title


# =====================================================
# ✅ Bank
# =====================================================
class Bank(models.Model):
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='images/')
    home_loan_partner = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '03. Bank'


# =====================================================
# ✅ Property Amenities
# =====================================================
class PropertyAmenities(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='property/amenities/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Property Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name

    def icon_tag(self):
        if self.icon:
            return mark_safe(f'<img src="{self.icon.url}" width="40" height="40" />')
        return ""

    icon_tag.short_description = "Icon"


# =====================================================
# ✅ Staff  (✅ FIXED: AUTH_USER_MODEL)
# =====================================================
class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# =====================================================
# ✅ Additional Info Response
# =====================================================
class AdditionalInfoResponse(models.Model):
    TYPE_CHOICES = (
        ('book_visit', 'Book Visit'),
        ('get_price', 'Get Price'),
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    visit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.name}"


# =====================================================
# ✅ Configuration Response
# =====================================================
class ConfigurationResponse(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    configuration = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.configuration} - {self.name}"


# =====================================================
# ✅ Brochure Lead
# =====================================================
class BrochureLead(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.project}"


# =====================================================
# ✅ Meta Lead
# =====================================================
class MetaLead(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    leadgen_id = models.CharField(max_length=100, unique=True)
    form_id = models.CharField(max_length=100, blank=True, null=True)
    page_id = models.CharField(max_length=100, blank=True, null=True)

    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    configuration = models.CharField(max_length=50, blank=True, null=True)
    budget = models.CharField(max_length=100, blank=True, null=True)
    visit_plan = models.CharField(max_length=100, blank=True, null=True)
    profession = models.CharField(max_length=120, blank=True, null=True)

    raw_payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"
