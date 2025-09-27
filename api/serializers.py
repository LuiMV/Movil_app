from rest_framework import serializers
from .models import Device, UsageRecord, Challenge, Questionnaire

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = '__all__'

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'

class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'
