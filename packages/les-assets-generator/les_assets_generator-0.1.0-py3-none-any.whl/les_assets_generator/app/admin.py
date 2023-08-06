from django.contrib import admin

from les_assets_generator.app.models import Asset, Parameter


class ParameterTabularInline(admin.TabularInline):
    model = Parameter
    extra = 1


class AssetAdmin(admin.ModelAdmin):
    inlines = [
        ParameterTabularInline,
    ]


admin.site.register(Asset, AssetAdmin)
