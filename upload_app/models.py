from django.db import models

# Create your models here.


class FileUpload(models.Model):
    """
    Represents a file upload with the file path and the timestamp of when it was uploaded.
    """
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
