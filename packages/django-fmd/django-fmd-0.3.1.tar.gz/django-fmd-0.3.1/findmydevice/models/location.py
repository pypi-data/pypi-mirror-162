import datetime
import logging

from django.db import models

from findmydevice.models import Device
from findmydevice.models.base import FmdBaseModel


logger = logging.getLogger(__name__)


class Location(FmdBaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    bat = models.CharField(max_length=256, unique=True)
    raw_date = models.PositiveBigIntegerField()
    lat = models.CharField(max_length=256, unique=True)
    lon = models.CharField(max_length=256, unique=True)
    provider = models.CharField(max_length=256, unique=True)

    def save(self, **kwargs):
        super().save(**kwargs)

        # Update "device.update_dt" field: So the admin change list will order the devices
        # by last location update ;)
        self.device.save(update_dt=True)

    @property
    def date_time(self) -> datetime.datetime:
        """
        Translates self.raw_date into a DateTime object
        """
        unix_time = self.raw_date / 1000
        dt = datetime.datetime.fromtimestamp(unix_time)
        logger.info('Raw date: %r -> %r -> %s', self.raw_date, unix_time, dt.isoformat())
        return dt

    def __str__(self):
        return f'Location {self.uuid} for {self.device} (Date: {self.raw_date}=={self.date_time})'

    def __repr__(self):
        return f'<{self.__str__()}>'

    class Meta:
        get_latest_by = ['create_dt']
