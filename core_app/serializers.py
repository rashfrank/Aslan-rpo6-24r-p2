from rest_framework import serializers
from .models import Ad, Category, City, Banner, Review

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'update_at', 'uuid')


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at', 'updated_at', 'user_username', 'can_edit']
        read_only_fields = ['user', 'ad', 'created_at']

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return obj.can_edit(request.user) if request and request.user.is_authenticated else False