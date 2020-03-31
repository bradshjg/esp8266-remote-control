import json

import pytest

from controller.api.serializers import Controller


def test_set_output(mocker, admin_client):
    mock_send = mocker.patch.object(Controller, 'send')
    response = admin_client.post('/api/output/', {'output': True}, content_type='application/json')
    msg = json.dumps({'out': 1})
    mock_send.assert_called_once_with(msg)
    assert response.status_code == 201


def test_set_position(mocker, admin_client):
    mock_send = mocker.patch.object(Controller, 'send')
    payload = {'pitch': 4, 'yaw': 7}
    response = admin_client.post('/api/position/', payload, content_type='application/json')
    mock_send.assert_called_once()
    assert payload == json.loads(mock_send.call_args_list[0][0][0])  # this is a goofy structure
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_recording(admin_client):
    payload = {'name': 'foo'}
    response = admin_client.post('/api/recordings/', payload, content_type='application/json')
    assert response.json() == {'id': 1, 'name': 'foo', 'user': {'username': 'admin'}, 'actions': []}


@pytest.mark.django_db
def test_add_action_to_recording(admin_client):
    recording_payload = {'name': 'foo'}
    admin_client.post('/api/recordings/', recording_payload, content_type='application/json')
    action_payload = {'actions': [{'payload': 'howdy'}]}
    response = admin_client.patch('/api/recordings/1/', action_payload, content_type='application/json')
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'name': 'foo', 'user': {'username': 'admin'}, 'actions': [{'payload': 'howdy'}]}
