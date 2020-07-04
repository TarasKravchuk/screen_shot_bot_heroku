from django.contrib import admin
from .models import *
# Register your models here.

myModels = [Messages]
admin.site.register(myModels)
