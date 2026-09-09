from rest_framework import serializers

from .models import CompetitionEditionAdmin, Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'code', 'name')


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CompetitionEditionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionEditionAdmin
        fields = ('id', 'user', 'competition_edition')
