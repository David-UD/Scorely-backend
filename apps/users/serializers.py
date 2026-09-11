from rest_framework import serializers

from .models import CompetitionAdmin, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CompetitionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionAdmin
        fields = ('id', 'user', 'competition', 'is_active', 'assigned_by', 'assigned_at')
        read_only_fields = ('assigned_at',)
