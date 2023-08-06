from django.contrib import admin

from .models import Location, Boundary


class LocationManager(admin.ModelAdmin):
    list_display = ['id', 'region_code', 'address', 'name', 'longitude', 'latitude', 'created_time']
    list_editable = ['address']
    search_fields = ['region_code', 'name', 'address']


class BoundaryManager(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


admin.site.register(Location, LocationManager)
admin.site.register(Boundary, BoundaryManager)
