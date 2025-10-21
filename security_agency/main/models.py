from django.db import models
from . import media
# Create your models here.

class Guard(models.Model):
    CATEGORY_CHOICES = [
        ('corporate', 'Corporate Security'),
        ('residential', 'Residential Security'),
        ('event', 'Event Security'),
    ]
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='media/', default='media/default.jpg')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    experience = models.PositiveIntegerField()
    skills = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='corporate')

    def __str__(self):
        return self.name
