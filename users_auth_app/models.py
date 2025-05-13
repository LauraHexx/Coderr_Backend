from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    """
    Represents a user profile with additional details for a user.
    Links to the default User model and includes fields for profile customization.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    location = models.CharField(
        max_length=255, null=False, blank=True, default='-')
    tel = models.CharField(max_length=20, null=False,
                           blank=True, default='-')
    description = models.TextField(
        null=False, blank=True, default='-')
    working_hours = models.CharField(
        max_length=50, null=False, blank=True, default='-')
    type = models.CharField(
        max_length=50, choices=[('business', 'Business'), ('customer', 'Customer')]
    )

    @property
    def username(self):
        """
        Returns the username of the associated user.
        """
        return self.user.username

    @property
    def email(self):
        """
        Returns the email address of the associated user.
        """
        return self.user.email

    @property
    def first_name(self):
        """
        Returns the first name of the associated user.
        """
        return self.user.first_name

    @property
    def last_name(self):
        """
        Returns the last name of the associated user.
        """
        return self.user.last_name

    @property
    def created_at(self):
        """
        Returns the date and time when the associated user account was created.
        """
        return self.user.date_joined
