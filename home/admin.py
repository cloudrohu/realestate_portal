from django.contrib import admin
from .models import (
    Setting, Slider, About_Page, Contact_Page,
    Our_Team, Testimonial, FAQ
)


# =============================
# 🌐 WEBSITE SETTINGS ADMIN
# =============================
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'meta_title', 'status', 'create_at')
    search_fields = ('site_name', 'meta_title', 'email')
    list_filter = ('status',)
    readonly_fields = ('logo_tag',)
    fieldsets = (
        ('🔹 Basic Info', {
            'fields': ('site_name', 'logo', 'logo_tag', 'favicon', 'search_bg', 'testmonial_bg')
        }),
        ('🎨 Theme Colors', {
            'fields': ('header_footer_color', 'text_color')
        }),
        ('📍 Contact Info', {
            'fields': ('address', 'phone', 'whatsapp', 'email', 'google_map')
        }),
        ('✉️ SMTP Configuration', {
            'fields': ('smtpserver', 'smtpemail', 'smtppassword', 'smtpport')
        }),
        ('💬 Social Links', {
            'fields': ('facebook', 'instagram', 'twitter', 'youtube')
        }),
        ('🔧 SEO & Footer', {
            'fields': ('meta_title', 'meta_description', 'footer_text', 'copy_right', 'status')
        }),
    )

    def logo_preview(self, obj):
        return obj.logo_tag()
    logo_preview.short_description = "Logo Preview"


# =============================
# 🖼️ SLIDER ADMIN
# =============================
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')
    list_filter = ('is_active',)
    ordering = ('order',)


# =============================
# ℹ️ ABOUT PAGE ADMIN
# =============================
@admin.register(About_Page)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')
    fieldsets = (
        ('🧾 About Section', {
            'fields': ('setting', 'title', 'subtitle', 'content', 'image')
        }),
    )


# =============================
# 📞 CONTACT PAGE ADMIN
# =============================
@admin.register(Contact_Page)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('heading', 'phone', 'email')
    search_fields = ('heading', 'address', 'email')
    fieldsets = (
        ('📍 Contact Information', {
            'fields': ('setting', 'heading', 'sub_heading', 'address', 'phone', 'email', 'map_iframe')
        }),
    )


# =============================
# 👨‍💼 OUR TEAM ADMIN
# =============================
@admin.register(Our_Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation')
    search_fields = ('name', 'designation')
    list_filter = ('designation',)
    fieldsets = (
        ('👨‍💼 Team Member Details', {
            'fields': ('setting', 'name', 'designation', 'image', 'bio')
        }),
    )


# =============================
# 💬 TESTIMONIAL ADMIN
# =============================
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'rating')
    search_fields = ('name', 'designation', 'message')
    list_filter = ('rating',)
    fieldsets = (
        ('💬 Testimonial Details', {
            'fields': ('setting', 'name', 'designation', 'message', 'image', 'rating')
        }),
    )


# =============================
# ❓ FAQ ADMIN
# =============================
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question', 'answer')
    fieldsets = (
        ('❓ Frequently Asked Question', {
            'fields': ('setting', 'question', 'answer')
        }),
    )
