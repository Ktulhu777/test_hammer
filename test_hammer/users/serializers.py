from re import fullmatch

from django.contrib.auth import get_user_model
from rest_framework import serializers


class CreateCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['phone']

    def validate_phone(self, phone: str) -> str:
        pattern = r'^(\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'
        if not fullmatch(pattern, phone):
            raise serializers.ValidationError(
                {'error': 'Invalid phone.'}
            )
        return phone


class LoginSerializer(serializers.Serializer):
    code = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    invited_by_code = serializers.CharField(write_only=True, required=False)  # Для ввода инвайт-кода
    invited_by = serializers.CharField(read_only=True)  # Для отображения, если уже введен
    invited_users = serializers.SerializerMethodField()  # Список приглашенных

    class Meta:
        model = get_user_model()
        fields = ['phone', 'unique_invite_code', 'invited_by', 'invited_by_code', 'invited_users']

    def get_invited_users(self, obj):
        return [user.phone for user in obj.invited_users.all()]

    def update(self, instance, validated_data):
        invited_by_code = validated_data.pop('invited_by_code', None)

        if invited_by_code == instance.unique_invite_code:
            raise serializers.ValidationError(
                {'error': 'Can"t enter your code.'}
            )
        if invited_by_code and not instance.invited_by:
            try:

                inviter = get_user_model().objects.get(unique_invite_code=invited_by_code)
                instance.invited_by = inviter
            except get_user_model().DoesNotExist:
                raise serializers.ValidationError(
                    {'error': 'Invalid invite code.'}
                )

        return super().update(instance, validated_data)
