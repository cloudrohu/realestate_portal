from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.safestring import mark_safe
from utility.compress_mixin import ImageCompressionMixin


# =============================
# 🧠 MAIN MODEL — Website Setting
# =============================
class Setting(ImageCompressionMixin, models.Model):


    
    site_name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    search_bg = models.ImageField(upload_to='logo/', blank=True, null=True)
    testmonial_bg = models.ImageField(upload_to='logo/')
    header_footer_color = models.CharField(max_length=150, blank=True)
    text_color = models.CharField(max_length=150, blank=True)

    address = models.CharField(blank=True, max_length=100)
    phone = models.CharField(blank=True, max_length=15)
    whatsapp = models.CharField(blank=True, max_length=15)
    email = models.CharField(blank=True, max_length=50)
    google_map = models.CharField(blank=True, max_length=1000)

    smtpserver = models.CharField(blank=True, max_length=50)
    smtpemail = models.CharField(blank=True, max_length=50)
    smtppassword = models.CharField(blank=True, max_length=10)
    smtpport = models.CharField(blank=True, max_length=5)


    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    footer_text = models.CharField(max_length=250, blank=True, null=True)
    copy_right = models.CharField(blank=True, max_length=100)


    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    
    
    

    facebook = models.CharField(blank=True, max_length=50)
    instagram = models.CharField(blank=True, max_length=50)
    twitter = models.CharField(blank=True, max_length=50)
    youtube = models.CharField(blank=True, max_length=50)

    status = models.CharField(max_length=10, choices=STATUS)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '0. Website Settings'

    def __str__(self):
        return self.site_name

    def logo_tag(self):
        if self.logo:
            return mark_safe(f'<img src="{self.logo.url}" width="100"/>')
        return "(No Logo)"


# =============================
# 🖼️ Hero / Slider Section (Multiple)
# =============================
class Slider(models.Model):
    setting = models.ForeignKey(Setting, on_delete=models.CASCADE, related_name='sliders')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='slider/')
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = '1. Slider Section'

    def __str__(self):
        return self.title


# =============================
# ℹ️ About Section (Single)
# =============================
class About_Page(models.Model):
    setting = models.OneToOneField(Setting, on_delete=models.CASCADE, related_name='about_section')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    content = RichTextUploadingField(blank=True, null=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True)

    class Meta:
        verbose_name_plural = '2. About Section'

    def __str__(self):
        return self.title


# =============================
# 📝 Contact Page (Single)
# =============================
class Contact_Page(models.Model):
    setting = models.OneToOneField(Setting, on_delete=models.CASCADE, related_name='contact_section')
    heading = models.CharField(max_length=200)
    sub_heading = models.CharField(max_length=300, blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    map_iframe = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = '3. Contact Page'

    def __str__(self):
        return self.heading


# =============================
# 👨‍💼 Our Team (Multiple)
# =============================
class Our_Team(models.Model):
    setting = models.ForeignKey(Setting, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = '4. Our Team'

    def __str__(self):
        return self.name


# =============================
# 💬 Testimonial Section (Multiple)
# =============================
class Testimonial(models.Model):
    setting = models.ForeignKey(Setting, on_delete=models.CASCADE, related_name='testimonials')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonial/', blank=True, null=True)
    rating = models.PositiveIntegerField(default=5)

    class Meta:
        verbose_name_plural = '5. Testimonials'

    def __str__(self):
        return f"{self.name} ({self.rating}⭐)"


# =============================
# ❓ FAQ Section (Multiple)
# =============================
class FAQ(models.Model):
    setting = models.ForeignKey(Setting, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = RichTextUploadingField()

    class Meta:
        verbose_name_plural = '7. FAQ Section'

    def __str__(self):
        return self.question
