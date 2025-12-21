from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('worker', 'Worker'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
