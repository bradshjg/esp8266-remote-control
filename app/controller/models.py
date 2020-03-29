from django.conf import settings
from django.db import models

from .device_controller import Controller


class RecordingQuerySet(models.QuerySet):
    def recent(self, limit=5):
        return self.order_by('-timestamp')[:limit]


class Recording(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recordings')
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = RecordingQuerySet.as_manager()


class ActionQuerySet(models.QuerySet):
    def replay(self):
        for action in self.order_by('-timestamp'):
            Controller.send(action.payload)
        return self


class Action(models.Model):
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE, related_name='actions')
    payload = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ActionQuerySet.as_manager()
