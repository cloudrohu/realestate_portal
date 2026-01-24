from django import template

register = template.Library()

@register.filter
def inr_short(value):
    try:
        value = float(value)
    except:
        return ""

    if value >= 10000000:  # 1 Crore
        return f"{value / 10000000:.2f} Cr"
    elif value >= 100000:  # 1 Lakh
        return f"{value / 100000:.0f} Lakh"
    else:
        return f"{int(value):,}"
