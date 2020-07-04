from django.db import models

# Create your models here.

class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    using_place = models.CharField(max_length=100, unique=True)
    message = models.CharField(max_length=400)

    def __str__(self):
        return f"№ {self.id} {self.using_place}"

    class Meta:
        ordering = ['-id']
