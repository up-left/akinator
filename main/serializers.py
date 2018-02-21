from rest_framework import serializers

from . import models


class GuessSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guess
        fields = ('id', 'name')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = ('id', 'name')
