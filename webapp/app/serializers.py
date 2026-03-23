from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'name', 'photo', 'photo_url', 'uploaded_at', 'owner']
        read_only_fields = ['id', 'uploaded_at', 'owner', 'photo_url']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if not obj.photo:
            return None
        url = obj.photo.url
        if request is None:
            return url
        return request.build_absolute_uri(url)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
