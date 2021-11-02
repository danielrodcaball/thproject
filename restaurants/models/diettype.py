from django.db import models


class DietType(models.Model):
    name = models.CharField(max_length=50, verbose_name='Diet Type')
