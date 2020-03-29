import json

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..device_controller import Controller
from ..models import Action, Recording


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username']


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['payload', 'timestamp', 'recording']


class RecordingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    actions = ActionSerializer(many=True, required=False)

    class Meta:
        model = Recording
        fields = ['id', 'name', 'user', 'actions']
        depth = 1

    def save(self, user):
        Recording.objects.create(user=user, **self.validated_data)

    def update(self, instance, validated_data):
        action_data = validated_data.pop('actions')
        for action in action_data:
            action = Action.objects.create(**action, recording=instance)
            instance.actions.add(action)
        return instance


class ActionBaseSerializer(serializers.Serializer):
    def get_payload(self):
        raise NotImplementedError('`get_payload` must be implemented.')

    def save(self, user=None):
        payload = self.get_payload()
        Controller.send(payload)

        recording_name = self.validated_data.get('recording')
        if recording_name:
            if not user:
                raise ValueError('Must supply the user to save actions to a recording.')
            action = Action(payload=payload)
            get_user_model().objects.get(id=user.id).recordings.get(name=recording_name).actions.add(action)


class OutputSerializer(ActionBaseSerializer):
    output = serializers.BooleanField()
    recording = serializers.CharField(max_length=255, required=False)

    def get_payload(self):
        return json.dumps({'out': 1 if self.validated_data['output'] else 0})


class PositionSerializer(ActionBaseSerializer):
    yaw = serializers.IntegerField(min_value=-45, max_value=45)
    pitch = serializers.IntegerField(min_value=-45, max_value=45)
    recording = serializers.CharField(max_length=255, required=False)

    def get_payload(self):
        return json.dumps({'yaw': self.validated_data['yaw'], 'pitch': self.validated_data['pitch']})
