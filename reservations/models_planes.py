from django.db import models
from django.contrib.auth.models import User

class ServiceClass(models.Model):
    name = models.CharField(max_length=100, blank=False)
    level = models.PositiveIntegerField()

class PlaneModel(models.Model):
    model_name = models.CharField(max_length=100, null=True)
    make_name = models.CharField(max_length=100, null=True)

class Plane(models.Model):
    plane_model = models.ForeignKey(PlaneModel, on_delete=models.PROTECT)

class PlaneSeat(models.Model):
    plane_model = models.ForeignKey(PlaneModel, on_delete=models.CASCADE)
    service_class = models.ForeignKey(ServiceClass,on_delete=models.PROTECT,related_name=None)
    serial_position = models.PositiveIntegerField()
    cabin_position = models.CharField(max_length=10, null=True)