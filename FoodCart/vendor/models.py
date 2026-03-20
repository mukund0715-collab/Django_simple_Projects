from django.db import models
from django.contrib.auth.models import User
import datetime, uuid


class FoodCart(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    
    # New: Photo for the Cart
    image = models.ImageField(upload_to='cart_images/', default='cart_images/default.jpg')
    
    # New: Opening/Closing Times
    opening_time = models.TimeField(default=datetime.time(10, 0)) # 10 AM
    closing_time = models.TimeField(default=datetime.time(22, 0)) # 10 PM
    
    # Manual Override (e.g., "Closed for emergency")
    is_open = models.BooleanField(default=True)

    current_lat = models.FloatField(default=12.9716)
    current_long = models.FloatField(default=77.5946)
    payment_qr = models.ImageField(upload_to='payment_qrs/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    cart = models.ForeignKey(FoodCart, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock_qty = models.IntegerField(default=20)
    
    # New: Photo for the Food Item
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
class CartSchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]

    cart = models.ForeignKey(FoodCart, on_delete=models.CASCADE, related_name='schedule')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    location_name = models.CharField(max_length=100) # e.g., "Main Campus Gate"
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.location_name}"
    

class OrderLobby(models.Model):
    # Generates a code like: "a1b2-c3d4"
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cart = models.ForeignKey(FoodCart, on_delete=models.CASCADE, related_name='lobbies', null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Lobby {self.code}"

class LobbyItem(models.Model):
    lobby = models.ForeignKey(OrderLobby, on_delete=models.CASCADE, related_name='items')
    # We store the name/price directly to keep it simple
    item_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    added_by = models.CharField(max_length=50) # Name of the user who clicked "Add"