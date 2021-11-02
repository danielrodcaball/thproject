from django.db import models


class DietType(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name')

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_name')
        ]
