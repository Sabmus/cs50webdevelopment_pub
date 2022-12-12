from django.contrib import admin

from . import models


class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("follower",)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Post)
admin.site.register(models.Comment)