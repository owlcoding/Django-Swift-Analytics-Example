from django.db import models

import hashlib
import datetime


# Create your models here.
from django.db.models import ExpressionWrapper, Min, Max, Count, F, DurationField


def random_hash():
    str = '{}'.format(datetime.datetime.now().timestamp())
    return hashlib.md5(bytes(str.encode())).hexdigest()


class Client(models.Model):
    client_platform = models.CharField(max_length=255, db_index=True)
    client_version = models.CharField(max_length=255, db_index=True)
    client_hash = models.CharField(max_length=2500, primary_key=True, default=random_hash, editable=False)

    def __str__(self):
        return "{} v. {} ({})".format(
            self.client_platform,
            self.client_version,
            self.client_hash
        )

class LogEvent(models.Model):
    id = models.AutoField(primary_key=True)
    event_name = models.CharField(db_index=True, max_length=255)
    event_time = models.DateTimeField(db_index=True, auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)

    def __str__(self):
        return "{}: {} ({})".format(self.event_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    self.event_name,
                                    ["{}: {}".format(x.param_name, x.param_value) for x in self.params.all()]
                                    )

    @staticmethod
    def sessions():
        return LogEvent\
            .objects\
            .values('client')\
            .annotate(min=Min('event_time'), max=Max('event_time'), number_of_log_entries=Count('id'))\
            .annotate(diff=ExpressionWrapper(F('max') - F('min'), output_field=DurationField()))\
            .order_by('-min')


class EventParam(models.Model):
    id = models.AutoField(primary_key=True)
    param_name = models.CharField(max_length=255, db_index=True)
    param_value = models.CharField(max_length=1400)
    event = models.ForeignKey(LogEvent, on_delete=models.CASCADE, related_name="params")
