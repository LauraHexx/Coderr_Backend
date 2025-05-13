from rest_framework import serializers
from upload_app.models import FileUpload


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializes file upload data, including the file and the timestamp of when it was uploaded.
    """
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']
