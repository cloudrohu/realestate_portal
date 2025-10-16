# home/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
from .models import Slider, About_Page, Contact_Page, Setting, Our_Team, Testimonial

# 📐 Thumbnail size
THUMBNAIL_SIZE = (300, 300)

# 💾 Max image size (2 MB)
MAX_SIZE_MB = 2

# ✅ Helper: get file size in MB
def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

# ✅ Helper: Compress + Thumbnail generator
def compress_and_thumbnail(image_path):
    if not image_path or not os.path.exists(image_path):
        return None, None

    img = Image.open(image_path)
    img = img.convert('RGB')

    # ⚡ Resize if file > 2MB
    if get_file_size_mb(image_path) > MAX_SIZE_MB:
        img.thumbnail((1600, 1600))  # resize while maintaining ratio

    # 🌐 WebP compress
    webp_path = image_path.rsplit('.', 1)[0] + '.webp'
    img.save(webp_path, format='WEBP', quality=70)

    # 📐 Generate Thumbnail
    thumb_img = img.copy()
    thumb_img.thumbnail(THUMBNAIL_SIZE)
    thumb_path = image_path.rsplit('.', 1)[0] + '_thumb.webp'
    thumb_img.save(thumb_path, format='WEBP', quality=80)

    # ❌ Delete original file
    if os.path.exists(image_path):
        os.remove(image_path)

    return webp_path, thumb_path

# ✅ Helper: apply compression to any field
def process_image_field(instance, field_name):
    image_field = getattr(instance, field_name)
    if image_field and not str(image_field).endswith('.webp'):
        webp_path, thumb_path = compress_and_thumbnail(image_field.path)
        if webp_path:
            relative_webp_path = image_field.name.rsplit('.', 1)[0] + '.webp'
            setattr(instance, field_name, relative_webp_path)
            instance.save(update_fields=[field_name])

        # 📝 Optional: store thumbnail path in a separate DB field if you want
        # For now we just generate it in media folder

# ✅ Slider
@receiver(post_save, sender=Slider)
def compress_slider_image(sender, instance, **kwargs):
    process_image_field(instance, 'image')

# ✅ About_Page
@receiver(post_save, sender=About_Page)
def compress_about_image(sender, instance, **kwargs):
    process_image_field(instance, 'image')

# ✅ Contact_Page
@receiver(post_save, sender=Contact_Page)
def compress_contact_image(sender, instance, **kwargs):
    process_image_field(instance, 'image')

# ✅ Setting (multiple image fields)
@receiver(post_save, sender=Setting)
def compress_setting_images(sender, instance, **kwargs):
    for field_name in ['logo', 'search_bg', 'testmonial_bg', 'icon']:
        process_image_field(instance, field_name)

# ✅ Our_Team
@receiver(post_save, sender=Our_Team)
def compress_team_image(sender, instance, **kwargs):
    process_image_field(instance, 'image')

# ✅ Testimonial
@receiver(post_save, sender=Testimonial)
def compress_testimonial_image(sender, instance, **kwargs):
    process_image_field(instance, 'image')