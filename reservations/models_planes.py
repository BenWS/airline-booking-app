from django.db import models
from django.contrib.auth.models import User

class PlaneModel(models.Model):
    pass

class Plane(models.Model):
    plane_model = models.ForeignKey(PlaneModel, on_delete=models.PROTECT)

class PlaneSeat(models.Model):
    plane_model = models.ForeignKey(PlaneModel, on_delete=models.CASCADE)
    service_class = models.ForeignKey(models.ServiceClass,on_delete=models.PROTECT,related_name=None)
    serial_position = models.PositiveIntegerField()
