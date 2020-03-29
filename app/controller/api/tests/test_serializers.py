import pytest

from controller.models import Action, Recording
from controller.api.serializers import ActionSerializer, Controller, OutputSerializer, PositionSerializer, RecordingSerializer


@pytest.fixture()
def recording(admin_user, db):
    recording_instance = Recording.objects.create(name='foo', user=admin_user)

    action_instance = Action.objects.create(payload='bar', recording=recording_instance)
    recording_instance.actions.add(action_instance)

    return recording_instance


def test_output_sends_message(mocker):
    mock_send = mocker.patch.object(Controller, 'send')
    serializer = OutputSerializer(data={'output': True})
    assert serializer.is_valid()
    serializer.save()
    assert mock_send.called_once_with({'out': 1})


def test_position_sends_message(mocker):
    mock_send = mocker.patch.object(Controller, 'send')
    serializer = PositionSerializer(data={'pitch': 0, 'yaw': 0})
    assert serializer.is_valid()
    serializer.save()
    assert mock_send.called_once_with({'pitch': 0, 'yaw': 0})


@pytest.mark.django_db
def test_recording_serialization_include_actions(recording):
    serialized = RecordingSerializer(instance=recording)
    assert serialized.data['actions'][0]['payload'] == 'bar'


@pytest.mark.django_db
def test_action_serializer_save(recording):
    serializer = ActionSerializer(data={'payload': 'foo', 'recording': recording.id})
    assert serializer.is_valid()
    serializer.save()

    assert recording.actions.count() == 2


@pytest.mark.django_db
def test_recording_serialization_add_action(recording):
    serialized = RecordingSerializer(instance=recording, data={'actions': [{'payload': 'baz'}]}, partial=True)
    assert serialized.is_valid()
    serialized.update(recording, serialized.validated_data)

    recording.refresh_from_db()
    assert recording.actions.latest('timestamp').payload == 'baz'
