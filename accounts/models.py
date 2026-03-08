"""Accounts models - Custom User for Nhimbe AI"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user model with farmer-specific fields"""

    PROVINCE_CHOICES = [
        ('harare', 'Harare'),
        ('bulawayo', 'Bulawayo'),
        ('manicaland', 'Manicaland'),
        ('mashonaland_central', 'Mashonaland Central'),
        ('mashonaland_east', 'Mashonaland East'),
        ('mashonaland_west', 'Mashonaland West'),
        ('masvingo', 'Masvingo'),
        ('matabeleland_north', 'Matabeleland North'),
        ('matabeleland_south', 'Matabeleland South'),
        ('midlands', 'Midlands'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('sn', 'Shona'),
        ('nd', 'Ndebele'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('none', 'Not Applied'),
        ('pending', 'Pending Review'),
        ('approved', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    bio = models.TextField(max_length=500, blank=True)
    province = models.CharField(max_length=30, choices=PROVINCE_CHOICES, blank=True)
    preferred_language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, default='en'
    )
    profile_picture = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )
    farming_experience = models.PositiveIntegerField(
        default=0, help_text="Years of farming experience"
    )
    crops = models.CharField(
        max_length=200, blank=True, help_text="Main crops e.g. maize, tobacco, groundnuts"
    )

    # AGRITEX Officer Verification
    is_agritex_officer = models.BooleanField(default=False)
    agritex_id_document = models.ImageField(
        upload_to='agritex_verification/',
        blank=True,
        null=True,
        help_text="Upload your AGRITEX ID or proof of employment"
    )
    agritex_verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='none'
    )
    agritex_verification_notes = models.TextField(
        blank=True,
        help_text="Admin notes about verification"
    )
    agritex_applied_at = models.DateTimeField(null=True, blank=True)
    agritex_verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_verified_agritex(self):
        """Check if user is a verified AGRITEX officer"""
        return self.is_agritex_officer and self.agritex_verification_status == 'approved'

    class Meta:
        verbose_name = 'Farmer'
        verbose_name_plural = 'Farmers'