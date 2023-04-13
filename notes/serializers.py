from rest_framework import serializers

from .models import User, Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('title', 'text')


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    def save(self, *args, **kwargs):
        data = self.validated_data
        user = User(
            email=data['email'],
            username=data['username']
        )
        password = data['password']
        password2 = data['password2']

        if password != password2:
            raise serializers.ValidationError({password: 'Пароль не совпадает'})

        user.set_password(password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']