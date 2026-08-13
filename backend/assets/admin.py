from django.contrib import admin

from .models import Batiment, Borne, SegmentRue

admin.site.register(Borne)
admin.site.register(Batiment)
admin.site.register(SegmentRue)