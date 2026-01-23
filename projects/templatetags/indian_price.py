from django import template

register = template.Library()

@register.filter
def indian_price(value):
    """
    Convert number into Indian format:
    12500000 => 1.25 Cr
    7500000  => 75 L
    95000    => 95 K
    """
    if value is None:
        return ""

    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if value >= 10000000:  # 1 Crore
        return f"{value / 10000000:.2f} Cr".rstrip("0").rstrip(".")
    elif value >= 100000:  # 1 Lakh
        return f"{value / 100000:.2f} L".rstrip("0").rstrip(".")
    elif value >= 1000:
        return f"{value / 1000:.0f} K"
    else:
        return str(int(value))
