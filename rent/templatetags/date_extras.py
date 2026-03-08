from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def smart_date(value):
    if not value:
        return ""

    now = timezone.now()
    today = now.date()
    value_date = value.date()

    if value_date == today:
        return "Today"
    elif value_date == today - timedelta(days=1):
        return "Yesterday"
    elif (today - value_date).days < 7:
        return f"{(today - value_date).days} days ago"
    else:
        return value.strftime("%d %b %Y")
