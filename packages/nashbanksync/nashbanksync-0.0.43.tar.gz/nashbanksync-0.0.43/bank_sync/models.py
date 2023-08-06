from django.db import models
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder


class Callbacks(models.Model):
    bank_id = models.IntegerField()
    type_code = models.IntegerField()
    reference = models.CharField(max_length=100,unique=True)
    callback = models.TextField()
    request = models.JSONField(default=dict)
    response = models.JSONField(default=dict)
    request_time = models.DateTimeField(default=timezone.now)
    response_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Callbacks(reference="{self.reference}",callback="{self.callback}", request={self.request}, response={self.response})'
