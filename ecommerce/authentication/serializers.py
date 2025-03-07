from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['id', 'email']  # Prevents modification of ID & Email

    def create(self, validated_data):
        """Creates a new user with hashed password"""
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Ensures password is hashed when updating"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
