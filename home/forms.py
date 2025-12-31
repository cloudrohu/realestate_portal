from django import forms
from .models import HomeContact

class HomeContactForm(forms.ModelForm):
    class Meta:
        model = HomeContact
        fields = ["name", "email", "phone", "type"]
