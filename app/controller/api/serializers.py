import json

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..device_controller import Controller
from ..models import Action, Recording


class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = ['name']
        depth = 2


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['payload', 'timestamp']


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
