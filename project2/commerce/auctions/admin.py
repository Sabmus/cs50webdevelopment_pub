from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.Category)
admin.site.register(models.BaseCurrency)
admin.site.register(models.Currency)
admin.site.register(models.Item)
admin.site.register(models.Bid)
admin.site.register(models.Comment)
admin.site.register(models.User)
