from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializes review data, including validation to ensure a reviewer can only review a business user once.
    """
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """Validates that a reviewer can only review a business user once."""
        request = self.context['request']
        if request.method == 'POST':
            reviewer = request.user
            business_user = data.get('business_user')
            if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
                raise serializers.ValidationError(
                    "You can only review a business user once.")
        return data
