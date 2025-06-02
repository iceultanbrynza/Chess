from django.contrib import admin

from .models import Player
# Register your models here.
@admin.register(Player)
class ProductItemAdmin(admin.ModelAdmin):
    readonly_fields=('id',)