from django.contrib import admin
from .models import (
    Setting, Slider, About_Page, Contact_Page,
    Our_Team, Testimonial, FAQ
)

# ================= Inline Classes =================

class SliderInline(admin.TabularInline):
    model = Slider
    extra = 1

class AboutInline(admin.StackedInline):
    model = About_Page
    extra = 0
    max_num = 1

class ContactInline(admin.StackedInline):
    model = Contact_Page
    extra = 0
    max_num = 1

class TeamInline(admin.TabularInline):
    model = Our_Team
    extra = 1

class TestimonialInline(admin.TabularInline):
    model = Testimonial
    extra = 1


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1


# ================= Main Admin =================
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'meta_title')
    inlines = [
        SliderInline,
        AboutInline,
        ContactInline,
        TeamInline,
        TestimonialInline,
        FAQInline,
    ]
