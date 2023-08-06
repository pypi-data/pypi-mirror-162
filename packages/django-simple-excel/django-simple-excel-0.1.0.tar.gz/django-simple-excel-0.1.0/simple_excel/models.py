from django.db import models


class ParentModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TestModel(models.Model):
    name = models.CharField(max_length=255, verbose_name="name")
    description = models.TextField(verbose_name="description")
    age = models.IntegerField()
    parent = models.ForeignKey(ParentModel, on_delete=models.CASCADE, null=True, blank=True)
