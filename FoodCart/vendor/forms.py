from django import forms
from django.contrib.auth.models import User
from .models import FoodCart, MenuItem, CartSchedule

class VendorRegistrationForm(forms.ModelForm):
    # Extra fields for the User model
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Field for the FoodCart model
    cart_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'stock_qty', 'image'] # Include image
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CartSettingsForm(forms.ModelForm):
    class Meta:
        model = FoodCart
        fields = ['image', 'payment_qr','opening_time', 'closing_time', 'is_open']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'payment_qr': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = CartSchedule
        fields = ['day_of_week', 'location_name', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. IT Park Gate 2'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }